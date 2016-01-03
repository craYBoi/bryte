$(document).ready( function() {
  // init Masonry
  var $grid = $('.grid').masonry({
    itemSelector: '.grid-item',
    percentPosition: true,
    columnWidth: '.grid-sizer'
  });
  // layout Isotope after each image loads
  $grid.imagesLoaded().progress( function() {
    $grid.masonry();
  });  

});

// $('.datepicker').datepicker({});

$('.emailinput, .textinput, .datetimeinput, .select, .textarea').addClass('form-control');
$('.control-group').addClass('form-group');