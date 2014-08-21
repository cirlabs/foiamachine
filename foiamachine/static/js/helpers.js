// Main menu sub menus

$('li.requests').click(function(event) {
    event.preventDefault();
    $('.requests-sub-menu').toggle('fast');
});

// Filters for requests or anything else

$('body').on('click', '.filter-toggle', function(){
    $('.filters').toggleClass('open');

});

$('body').on('change', '#check_all_requests', function(){
    var $this = $(this);

    $('#action_form input.request_check').prop('checked', $this.prop('checked'));

});
