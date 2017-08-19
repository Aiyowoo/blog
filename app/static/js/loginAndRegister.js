$(document).ready(function() {
    $("#register-button").click(function() {
        $("#register-li").addClass('active');
        $("#register").css('display', '');
        $("#login-li").removeClass('active');
        $("#login").css('display', 'none');
    });
    $("#login-button").click(function() {
        $("#register-li").removeClass('active');
        $("#register").css('display', 'none');
        $('#login-li').addClass('active');
        $('#login').css('display', '');
    });
});
