$(document).ready(function(){



	




	menuWidth = $('#main-menu').width()
	
	hideMenu();


	function hideMenu(){
		$( "#main-menu" ).animate({
			left: -menuWidth+37
		}, 300, function() {
		    // Animation complete.
		});	
	}

	function showMenu(){
		$( "#main-menu" ).animate({
			left: "1em"
		}, 100, function() {
		    // Animation complete.
		});
	}


	$( "#main-menu" ).hover(function(){
		showMenu();
	}, function(){
		hideMenu();
	}).click(function(){
		showMenu();
	})

	



});

