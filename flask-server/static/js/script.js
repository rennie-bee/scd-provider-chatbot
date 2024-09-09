// static/js/script.js

function sendMessage() {
    var userInput = document.getElementById('userInput').value;
    if (userInput.trim() === '') {
        alert('Please enter a message.');
        return;
    }

    $.ajax({
        url: '/chat/1x2abc/1',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ user_input: userInput }),
        success: function(data) {
            $('#chatbox').append('<p><strong>You:</strong> ' + userInput + '</p>');
            $('#chatbox').append('<p><strong>Bot:</strong> ' + data.response + '</p>');
            document.getElementById('userInput').value = ''; // Clear input field
        },
        error: function() {
            alert('Error sending message');
        }
    });
}

