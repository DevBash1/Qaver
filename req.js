function req() {
    let Req = this;
    let xhr;
    let response;
    let error;
    let reqHeaderName = "Content-type";
    let reqHeaderBody = "application/x-www-form-urlencoded";

    function formatResponse(data) {
        return data;
    }
    if (window.XMLHttpRequest) {
        // code for modern browsers
        xhr = new XMLHttpRequest();
    } else {
        // code for old IE browsers
        xhr = new ActiveXObject("Microsoft.XMLHTTP");
    }

    this.setRequestHeader = function(name, header) {
        reqHeaderName = name;
        reqHeaderBody = header;
    }

    this.onError = function(err) {
        error = err;
    }

    this.get = function(url, callback) {
        if (url != undefined) {
            if (callback == undefined) {
                xhr.onload = function() {
                    if (xhr.status == 200) {
                        response = xhr.responseText;
                        Req.status = xhr.status;
                        Req.response = xhr.response || xhr.responseText;
                    } else {
                        if (error) {
                            error(xhr.status, xhr.responseText);
                        }
                    }
                }
                xhr.onerror = function(err) {
                    if (error) {
                        error(xhr.status, err);
                    }
                }
                xhr.open("GET", url, false);
                xhr.setRequestHeader(reqHeaderName, reqHeaderBody);
                xhr.send();
                return response;
            } else {
                xhr.onload = function() {
                    if (xhr.status == 200) {
                        response = xhr.responseText;
                        Req.status = xhr.status;
                        Req.response = xhr.response || xhr.responseText;
                        callback(formatResponse(response), xhr.status);
                    } else {
                        if (error) {
                            error(xhr.status, xhr.responseText);
                        }
                    }
                }
                xhr.onerror = function(err) {
                    if (error) {
                        error(xhr.status, err);
                    }
                }
                xhr.open("GET", url, true);
                xhr.setRequestHeader(reqHeaderName, reqHeaderBody);
                xhr.send();
            }
        }
        return Req;
    }
    this.send = function(url, options) {
        if (url != undefined) {
            if (options != undefined) {
                let type;
                let hasSuccess = false;
                let hasError = false;
                let params = "";

                if (options.type || options.method != undefined) {
                    type = options.type.toUpperCase().trim() || options.method.toUpperCase().trim();
                } else {
                    type = "POST";
                }

                if (options.params || options.param != undefined) {
                    params = options.params || options.param;
                }

                if (type == "GET") {
                    url += "?" + params;
                }

                if (options.success != undefined) {
                    hasSuccess = options.success;
                    if (typeof hasSuccess != "function") {
                        throw ("success must be of type function");
                    }
                }

                if (options.error != undefined) {
                    hasError = options.error;
                    if (typeof hasError != "function") {
                        throw ("error must be of type function");
                    }
                }

                xhr.onload = function() {
                    if (xhr.status == 200) {
                        response = xhr.responseText;
                        Req.status = xhr.status;
                        Req.response = xhr.response || xhr.responseText;
                        if (hasSuccess) {
                            hasSuccess(response);
                        }
                    } else {
                        if (hasError) {
                            hasError(xhr.status, xhr.responseText);
                        }
                    }
                }
                xhr.onerror = function(err) {
                    if (hasError) {
                        hasError(xhr.status, xhr.responseText);
                    }
                }

                xhr.open(type, url, true);
                xhr.setRequestHeader(reqHeaderName, reqHeaderBody);
                if (type != "GET") {
                    xhr.send(params);
                } else {
                    xhr.send();
                }
            }
        }
        return Req;
    }
    async function poll(url,cb,err) {
        let response =  await fetch(url);

        if (response.status == 502) {
            // Status 502 is a connection timeout error,
            // may happen when the connection was pending for too long,
            // and the remote server or a proxy closed it
            // let's reconnect
            await poll();
        } else if (response.status != 200) {
            // An error
            if(typeof err == "function"){
                err(response.status);
            }
            // Reconnect in one second
            await new Promise(resolve=>setTimeout(resolve, 1000));
            await poll();
        } else {
            // Get the message
            let message = await response.text();
            if(typeof cb == "function"){
                cb(message);
            }
        }
        try {
            await poll();
        } catch (e) {

        }
    }
    this.poll = function(url,options){
        if(url != undefined){
            if(options != undefined){
                if(options.success != undefined){
                    if(options.error != undefined){
                        poll(url,options.success,options.error);
                    }else{
                        poll(url,options.success);
                    }
                }
            }
        }
    }
}
