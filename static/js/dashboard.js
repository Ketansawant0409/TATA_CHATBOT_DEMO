$(document).ready(function() {
    $('#chat-form').submit(function(e) {
        e.preventDefault();
        var selectedQuestion = $('#question').val();
        
        // Display the progress bar
        $('#progress').show();
        
        $.ajax({
            type: 'POST',
            url: '/dashboard', // Update the URL to match your Flask route
            data: { 'question': selectedQuestion },
            xhr: function() {
                var xhr = new window.XMLHttpRequest();
                xhr.upload.addEventListener("progress", function(evt) {
                    if (evt.lengthComputable) {
                        var percentComplete = (evt.loaded / evt.total) * 100;
                        $('.progress-bar').width(percentComplete + '%');
                        $('.progress-bar').attr('aria-valuenow', percentComplete);
                    }
                }, false);
                return xhr;
            },
            success: function(data) {
                // Hide the progress bar
                $('#progress').hide();
                
                // Update the answer without reloading the page
                $('#answer').html('<p>' + data.answer + '</p>');
            },
            error: function(error) {
                // Hide the progress bar
                $('#progress').hide();
                
                console.log(error);
            }
        });
    });
});


function copyToClipboard() {
    var answerText = $('#answer p').text();
    
    navigator.clipboard.writeText(answerText)
        .then(function() {
            alert('Answer copied to clipboard!');
        })
        .catch(function(err) {
            console.error('Unable to copy to clipboard: ', err);
        });
}


function clearAnswer() {
    $('#answer').empty();
}