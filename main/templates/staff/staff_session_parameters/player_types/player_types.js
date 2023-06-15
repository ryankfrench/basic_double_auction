/**show edit parameter set player
 */
show_edit_parameter_set_player_type:function(index){
    
    if(app.session.started) return;
    if(app.working) return;

    app.clear_main_form_errors();
    app.current_parameter_set_player_type = Object.assign({}, app.parameter_set.parameter_set_player_types[index]);
    
    app.edit_parameterset_player_type_modal.toggle();
},

/** update parameterset player
*/
send_update_parameter_set_player_type(){
    
    app.working = true;

    app.send_message("update_parameter_set_player_type", {"session_id" : app.session.id,
                                                          "parameterset_player_type_id" : app.current_parameter_set_player_type.id,
                                                          "form_data" : app.current_parameter_set_player_type});
},

/** remove the selected parameterset player
*/
send_remove_parameter_set_player_type(){

    app.working = true;
    app.send_message("remove_parameterset_player_type", {"session_id" : app.session.id,
                                                    "parameterset_player_type_id" : app.current_parameter_set_player_type.id,});
                                                   
},

/** add a new parameterset player
*/
send_add_parameter_set_player_type(player_type_id){
    app.working = true;
    app.send_message("add_parameterset_player_type", {"session_id" : app.session.id});
                                                   
},