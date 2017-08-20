$(document).ready(function() {
    $("#register-button").click(function() {
        $("#register-li").addClass('active');
        $("#register").css('display', '');
        $("#login-li").removeClass('active');
        $("#login").css('display', 'none');
        $("#login [data-toggle='popover']").popover('hide');
        $("#register [data-toggle='popover']").popover('show');
    });

    $("#login-button").click(function() {
        $("#register-li").removeClass('active');
        $("#register").css('display', 'none');
        $('#login-li').addClass('active');
        $('#login').css('display', '');
        $("#register [data-toggle='popover']").popover('hide');
        $("#login [data-toggle='popover']").popover('show');
    });

    $('[data-toggle="popover"]').change(function(event) {
        $(event.target).popover('destroy');
        $(event.target).removeAttr('data-toggle');
    });

    init();

});
