$(document).ready(function(){


    $('#log-table').dataTable();

    $('body').on('click.collapse-next.data-api', '[data-toggle=collapse-next]', function() {
	var $target = $(this).next()
	$target.data('toggle') ? $target.collapse('collapse') : $target.toggle()    
});



});