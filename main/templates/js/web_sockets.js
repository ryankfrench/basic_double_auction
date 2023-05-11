//web sockets, needs should be included with companion vue.js app
do_web_sockets = function()
{
        let ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
        app.chat_socket = new WebSocket(            
                               ws_scheme + '://' + window.location.host +
                               '/ws/{{websocket_path}}/{{channel_key}}/{{page_key}}/{{player_key}}');        
    
        app.chat_socket.onmessage = function(e) {
            let data = JSON.parse(e.data);                       
            app.take_message(data);
        };
    
        app.chat_socket.onclose = function(e) {
            console.error('Socket closed, trying to connect ... ');

            app.reconnecting=true;
            if(!app.handle_socket_connection_try()) 
            {
                console.error('Socket re-connection limit reached.');
                return;
            } 
            window.setTimeout(do_web_sockets(), random_number(500,1500));            
        }; 

        app.chat_socket.onopen = function(e) {
            console.log('Socket connected.');     
            app.reconnecting=false;   
            app.handle_socket_connected();                      
        };                
};

random_number = function(min, max){
    //return a random number between min and max
    min = Math.ceil(min);
    max = Math.floor(max+1);
    return Math.floor(Math.random() * (max - min) + min);
};

do_web_sockets();