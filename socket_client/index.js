const io = require('socket.io-client');

const socket = io('http://localhost:8000', {query:'uid=ID1'},autoConnect=false);

socket.on('Notification',function(args,callback) {
	console.log('Notified !');
	// Give callback with the _id and set state to fulfilled i.e. 1
	callback(JSON.parse(args)['_id'],1);
});

socket.on('connect', function(args) {
	console.log('Connected');
	console.log(args);
});

socket.on('disconnect', function(args) {
	console.log('Disconnected');
});

socket.open();

