#!/usr/bin/env python3
"""This module contains internal routines used by the guidance computer."""


from basagc import utils, config
if config.DEBUG:
    from pudb import set_trace  # lint:ok
    
def charin(keypress, state, dsky, computer):
    '''
    This function is called whenever a keypress is sent from the UI. 
    :param keypress: What key was pressed
    :type keypress: str
    :param state: the dsky and computer state relevant to dsky operations
    :type state: dict
    :param dsky: the instance of the dsky
    :type dsky: basagc.dsky.DSKY
    :param computer: the instance of the computer
    :type computer: basagc.computer.Computer
    :returns: None
    '''
    
    def handle_control_register_load():
        
        """ Handles control register loading
        :returns: None
        """
        # we are expecting a numeric digit as input
        if keypress.isalpha():
            computer.operator_error("Expecting numeric input")
            return
        # otherwise, add the input to buffer
        display_register = state["display_location_to_load"]
        if state["register_index"] == 0:
            dsky.set_register(keypress, display_register, "1")
            #display_register["1"].display(keypress)
            state["input_data_buffer"] = keypress
            state["register_index"] += 1
        else:
            dsky.set_register(keypress, display_register, "2")
            state["register_index"] = 0
            state["input_data_buffer"] += keypress
            
    
    def handle_data_register_load():
    
        """ Handles data register loading
        :return: None
        """
        if keypress.isdigit() == False:
            utils.log("Expecting a digit for data load, got {}".format(keypress), log_level="ERROR")
            return
        display_register = state["display_location_to_load"]
        if state["register_index"] == 0:
            if keypress == "+":
                dsky.set_register("+", display_register)
            elif keypress == "-":
                dsky.set_register("-", display_register)
            else:
                dsky.set_register("b", display_register)
            state["register_index"] += 1
        if 1 <= state["register_index"] <= 5:
            dsky.set_register(keypress, display_register, digit=state["register_index"])
            if state["register_index"] >= 5:
                state["register_index"] = 0
            else:
                state["register_index"] += 1
        state["input_data_buffer"] += keypress

    def handle_expected_data():
    
        """ Handles expected data entry.
        :return: None
        """
        #set_trace()
        if keypress == "P":
            dsky.verb_noun_flash_off()
            utils.log("Proceeding without input, calling {}".format(str(state["object_requesting_data"])))
            state["object_requesting_data"]("proceed")
            state["input_data_buffer"] = ""
            state["is_expecting_data"] = False
            return
    
        # if we receive ENTER, the load is complete and we will call the
        # program or verb requesting the data load

        elif keypress == "E":
            input_data = state["input_data_buffer"]
            state["input_data_buffer"] = ""
            state["is_expecting_data"] = False
            dsky.verb_noun_flash_off()
            data_requester = state["object_requesting_data"]
            utils.log("Data load complete, calling {}({})".format(data_requester.__self__, data_requester.__name__))
            data_requester(input_data)
            
            return
        if state["display_location_to_load"] in ["verb", "noun", "program"]:
            handle_control_register_load()
        else:
            handle_data_register_load()
    
        # if the user as entered anything other than a numeric d,
        # trigger a OPR ERR and recycle program
        if keypress.isalpha():
            # if a program is running, recycle it
            # INSERT TRY HERE!!!
            # computer.get_state("running_program").terminate()
            # INSERT EXCEPT HERE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            # if a verb is running, recycle it
            # computer.get_state("running_verb").terminate()
            computer.operator_error("Expecting numeric input")
            return
        #else:
            #print(state["input_data_buffer"])
            #state["input_data_buffer"] += keypress
            #print(state["input_data_buffer"])
            #register = state["display_location_to_load"]
            #dsky.set_register(state["input_data_buffer"], register)
        


    def handle_verb_entry():
    
        """ Handles verb entry
        :return: None
        """
    
        if keypress == "C":  # user has pushed CLEAR
            state["verb_position"] = 0
            state["requested_verb"] = ""
            dsky.blank_register("verb")
            dsky.blank_register("noun")
            #dsky.control_registers["verb"].digits[1].display("blank")
            #dsky.control_registers["verb"].digits[2].display("blank")
            return
    
        if keypress == "N":  # user has finished entering verb
            state["is_verb_being_loaded"] = False
            state["is_noun_being_loaded"] = True
            state["verb_position"] = 0
        elif keypress == "E":
            state["is_verb_being_loaded"] = False
            state["verb_position"] = 0
        elif keypress.isalpha():
            computer.operator_error("Expected a number for verb choice")
            return
        elif state["verb_position"] == 0:
            dsky.set_register(value=keypress, register="verb", digit="1")
            state["requested_verb"] = keypress
            state["verb_position"] = 1
        elif state["verb_position"] == 1:
            dsky.set_register(value=keypress, register="verb", digit="2")
            state["requested_verb"] += keypress
            state["verb_position"] = 2

    def handle_noun_entry():
    
        """ Handles noun entry.
        :return: None
        """
    
        if keypress == "C":  # user has pushed CLEAR
            state["noun_position"] = 0
            state["requested_noun"] = ""
            dsky.control_registers["noun"].digits[1].display("blank")
            dsky.control_registers["noun"].digits[2].display("blank")
            return
    
        if keypress == "N":  # user has finished entering noun
            state["is_noun_being_loaded"] = False
            state["is_verb_being_loaded"] = True
            state["noun_position"] = 0
        elif keypress == "E":
            state["is_noun_being_loaded"] = False
            state["noun_position"] = 0
        elif keypress.isalpha():
            computer.operator_error("Expected a number for noun choice")
            return
        elif state["noun_position"] == 0:
            dsky.set_register(keypress, "noun", digit="1")
            state["requested_noun"] = keypress
            state["noun_position"] = 1
        elif state["noun_position"] == 1:
            dsky.set_register(keypress, "noun", digit="2")
            state["requested_noun"] += keypress
            state["noun_position"] = 2

    def handle_entr_keypress():
    
        """ Handles ENTR keypress
        :return: None
        """
    
        computer.execute_verb()
        state["requested_noun"] = ""

    def handle_reset_keypress():
    
        """ Handles RSET keypress
        :return: None
        """
    
        computer.reset_alarm_codes()
        dsky.reset_annunciators()
        if dsky.annunciators["opr_err"].blink_timer.isActive():
            dsky.annunciators["opr_err"].stop_blink()

    def handle_noun_keypress():
    
        """ Handles NOUN keypress
        :return: None
        """
    
        state["is_verb_being_loaded"] = False
        state["is_noun_being_loaded"] = True
        state["requested_noun"] = ""
        dsky.blank_register("noun")

    def handle_verb_keypress():
    
        """ Handles VERB keypress
        :return: None
        """
    
        state["is_noun_being_loaded"] = False
        state["is_verb_being_loaded"] = True
        state["requested_verb"] = ""
        dsky.blank_register("verb")

    def handle_key_release_keypress():
    
        """ Handles KEY REL keypress
        :return: None
        """
        if state["backgrounded_update"]:
            backgrounded_update = state["backgrounded_update"].resume
            if state["display_lock"]:
                state["display_lock"].terminate()
            dsky.stop_annunciator_blink("key_rel")
            backgrounded_update()
            state["backgrounded_update"] = None
            state["is_verb_being_loaded"] = False
            state["is_noun_being_loaded"] = False
            state["is_data_being_loaded"] = False
            state["verb_position"] = 0
            state["noun_position"] = 0
            state["requested_verb"] = ""
            state["requested_noun"] = ""
            return
    
    # if the computer is off, we only want to accept the PRO key input,
    # all other keys are ignored
    if computer.is_powered_on == False:
        if keypress == "P":
            computer.on()
        else:
            utils.log("Key {} ignored because gc is off".format(keypress))
            return
    
    if state["is_expecting_data"]:
        handle_expected_data()
        return
    
    if keypress == "R":
        handle_reset_keypress()
        return
    
    if keypress == "K":
        handle_key_release_keypress()
        return
    
    if state["display_lock"]:
        state["display_lock"].background()
    
    if state["is_verb_being_loaded"]:
        handle_verb_entry()
    
    elif state["is_noun_being_loaded"]:
        handle_noun_entry()
    
    if keypress == "E":
        handle_entr_keypress()
    
    if keypress == "V":
        handle_verb_keypress()
    
    if keypress == "N":
        handle_noun_keypress()
    
    if keypress == "C":
        pass  # TODO

