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

  // photographer detail page switch tab
});


// enable smooth scroll
$(function() {
  $('a[href*=#]:not([href=#])').click(function() {
    if (location.pathname.replace(/^\//,'') == this.pathname.replace(/^\//,'') && location.hostname == this.hostname) {
      var target = $(this.hash);
      target = target.length ? target : $('[name=' + this.hash.slice(1) +']');
      if (target.length) {
        $('html,body').animate({
          scrollTop: target.offset().top
        }, 800);
        return false;
      }
    }
  });
});

$(document).ready(function(){
  
  //Check to see if the window is top if not then display button
  if ($('.scrollToTop').offset().top > 200) {
    $('.scrollToTop').hide();
  }
  $(window).scroll(function(){
    if ($(this).scrollTop() > 200) {
      $('.scrollToTop').fadeIn();
    } else {
      $('.scrollToTop').fadeOut();
    }
  });
  
  //Click event to scroll to top
  $('.scrollToTop').click(function(){
    $('html, body').animate({scrollTop : 0},800);
    return false;
  });
  
});

// navbar color transition
// var mainbottom = $('#main').offset().top + $('#main').height();

// // on scroll, 
// $(window).on('scroll',function(){

//     // we round here to reduce a little workload
//     stop = Math.round($(window).scrollTop());
//     if (stop > mainbottom) {
//         $('.nav').addClass('past-main');
//     } else {
//         $('.nav').removeClass('past-main');
//    }

// });

// add datetimepicker to id=id_datetime
$(document).ready(function(){
  $('#id_datetime').attr('id', 'datetimepicker');
});

