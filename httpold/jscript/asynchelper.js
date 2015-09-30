/* This is using the new REST API */
function asynchelper(argpersistence, argautostart) {
    // AsyncHelper created by Mikael Aspehed. Can be found on Github, Dagalufh.  Inspiration from Async for NodeJS. 
    var object = this;
    
    // variables, don't call these directly.
    this.completefunction = '';
    this.currentindex = -1;
    this.functionsarray = [];
    this.persistent = false;
    this.result = [];
    this.autostart = true;
    
    if (typeof(argpersistence) != 'undefined') {
        this.persistent = argpersistence;
    }
    
    if (typeof(argautostart) != 'undefined') {
        this.autostart = argautostart;
    }
    
    // Callback function. Don't call this one directly either. Must be triggered inside the supplied functions.
    this.callback = function(result, arguments) {
        object.result.push(result);
        // Execute next in the series.
        if (object.persistent === true) {
            object.currentindex = object.currentindex+1;
            if (object.currentindex < object.functionsarray.length) {
                object.functionsarray[object.currentindex](object.callback,arguments);
            } else {
                object.currentindex = -1;
                if (typeof(object.completefunction) == 'function') {
                    object.completefunction(object.result,arguments);
                }
            }            
        } else {
            
            if (object.functionsarray.length > 0) {
                var currentfunction = object.functionsarray.shift();
                currentfunction(object.callback,arguments);
            } else {
                if (typeof(object.completefunction) == 'function') {
                    object.completefunction(object.result,arguments);
                }
            }
        }
    };
    
    // This is the main function, call this and supply functions as an array in the first argument. Second argument is a function to be run on completion.
    this.inline = function(functionslist,complete) {
        object.functionsarray = functionslist;
        object.completefunction = complete;
        object.result = [];
        if (object.autostart === true) {
            object.callback('autostart',this.callback);
        }
    };
    
    // Used to rerun the supplied functions if persistance mode is on.
    this.start = function(argument) {
        if (object.functionsarray.length > 0) {
            object.result = [];
            object.callback('manualstart',argument);  
        } else {
            console.log('There wasn\'t any functions to run.');
        }
    };
    
    // Used to control if persistance should be on or off.
    // This is usefull if you want to re-run the same inline series multiple times.
    this.setpersistence = function(value) {
        object.persistent = value;
    }
    
    // Returns the results. The results are stored in an array in the order the functions are executed.
    // So to access the result of the previously running function: classinstance.getresults()[classinstance.getresults().length-1]);
    this.getresults = function() {
        return object.result;
    };
    
    // Setting this to false allows to define the inline functionlist without running the functions right away. They can be run afterwards with the start function.
    this.setautostart = function(value) {
        object.autostart = value;
    }
    
    // Allows the skip of the rest of the functions and jumps instantly to the complete function if one is available.
    this.jumptocomplete = function(result, arguments) {
        object.result.push(result);
        object.currentindex = -1;
        if (typeof(object.completefunction) == 'function') {
            object.completefunction(object.result,arguments);
        }
    }
    
    // Abort
    this.abort = function(result) {
        object.result.push(result);
        object.currentindex = -1;
    }
}


