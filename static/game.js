$(document).ready(function() {
    $('form').on('submit', function(e) {
        e.preventDefault();
        var form = $(this);
        var questionIndex = form.attr('id').replace('question', '');
        var answer = form.find('input[type=text]').val();
        $.ajax({
            url: '/answers/' + questionIndex + '?answer=' + encodeURIComponent(answer),
            type: 'POST',
            success: function(data) {
                if (data.correct) {
                    form.find('input[type=submit]').prop('disabled', true);
                    form.find('input[type=text]').prop('readonly', true);
                    form.find('input[type=submit]').val('Correct');
                } else {
                    form.find('input[type=text]').addClass('shake-animation');
                    form.find('input[type=text]').on('animationend', function() {
                        $(this).removeClass('shake-animation');
                    });
                    form.find('input[type=submit]').val('Try again');
                }
                if (data.final) {
                    showCongratulationsModal();
                }
            }
        });
    });

    $('.hint-button').on('click', function(e) {
        e.preventDefault();
        var button = $(this);
        var questionIndex = button.data('question-index');
        var hintIndex = $('form#question' + questionIndex).data('hint-index');
        $.ajax({
            url: '/hints/' + questionIndex,
            type: 'GET',
            success: function(data) {
                var hintHtml = '<p>💡 ' + data.hint + '</p>';
                $('#question' + questionIndex + '_hints').append(hintHtml);
                if (data.last) {
                    button.prop('disabled', true);
                    button.text('No more hints available');
                }       
            }
        });
    });
    // Show congratulations modal
    function showCongratulationsModal() {
        var modal = document.getElementById('congratulations-modal');
        modal.style.display = 'block';
    }

    // Close modal event handler
    $('.close').on('click', function() {
        hideCongratulationsModal();
    });

    // Hide congratulations modal
    function hideCongratulationsModal() {
        var modal = document.getElementById('congratulations-modal');
        modal.style.display = 'none';
    }
});