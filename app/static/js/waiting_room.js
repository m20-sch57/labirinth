function xhrOpen(eventType) {
	var xhr = new XMLHttpRequest();

	xhr.open('POST', document.getElementById('data').dataset.post, false);
	xhr.setRequestHeader('Event-Type', eventType);
	xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');

	return xhr;
};
function changeDescription(event) {
	if (event.keyCode == 13){
		var xhr = xhrOpen('change_description');
		var newDescription = document.getElementById('room_description').value;

		xhr.send("new_description=" + newDescription);	
	};
};
function changeName(event) {
	if (event.keyCode == 13){
		var xhr = xhrOpen('change_name');
		var newName = document.getElementById('room_name').value;

		xhr.send("new_name=" + newName);
	};
};
function startGame() {
	var xhr = xhrOpen('start_game');
	
	xhr.send();
};

var socket = io.connect('http://' + document.domain + ':' + location.port + '/wrws');
socket.on('update', function(msg) {
	switch (msg.event) {
		case 'change_name':
			var title = document.getElementById('title');
			title.innerHTML = (msg.name);
			break;
		case 'player_enter_or_leave':
			var player_list = document.getElementById('player_list');
			player_list.innerHTML = '';
			for (var i = 0; i < msg.players.split(',').length; i++) {
				player_list.innerHTML += ('<p class="player">' + msg.players.split(',')[i] + '</p><hr>')
			};
			break;
		case 'change_description':
			var description = document.getElementById('description');
			description.innerHTML = ('Description:<br>' + msg.description.replace(/\n/g, '<br>'));
			break;
		case 'start_game':
			document.location.href = document.getElementById('data').dataset.redirect;
			break;
	};
});
socket.on('connect', function() {
	socket.emit('player join', {'room_id': document.getElementById('data').dataset.room_id});
});

var changeNameInput = document.getElementById('room_name');
changeNameInput.onkeydown = changeName;

var changeDescriptionInput = document.getElementById('room_description');
changeDescriptionInput.onkeydown = changeDescription;

var startButton = document.getElementById('start_button');
startButton.onclick = startGame;

var settingButton = document.getElementById('settings_button');
var roomInfo = document.getElementById('room_info');
var roomSettings = document.getElementById('room_settings');
settingButton.onclick = function() {
	toggle(roomInfo);
	toggle(roomSettings);
};