$(function(){
    var element_pos = 0;    // Position of the newly created elements.
    var iCnt = 0;
    var iCnt2 = 0;
    var order_prep = $('#Order-Prep');
    var order_exec = $('.Order-Execution');
    prelim_prep_instruction = '';
    prelim_exec_instruction = '';
    $(document).ready(function() {
        //PREP Column
          $(function() { $('#divContainer').draggable(); });
          $(function() { $('#divContainer-drop').droppable(); });
          // Create more DIV elements with absolute postioning.
          $(document).keydown(function(event) {
            //window.alert(event.keyCode);
            if (event.keyCode =='40'){
              var dynamic_div = $(document.createElement('div')).css(
                "margin-left", "100px"
              );
              var dynamic_div2 = $(document.createElement('div')).css(
                "margin-left", "100px"
              );
            var input_value = '';
            var input_value_execution = '';
            input_value = $('#holder-input-prep').val();
            if (input_value !=''){
              $(dynamic_div).append("<li >"+input_value+"</li>");
              $(dynamic_div).text()
              $('#holder-input-prep').val("");
              // Append the newly created DIV to the container.
              $(dynamic_div).appendTo('#divContainer').draggable(
                {
                  cursor: "move",
                  drag: function( event, ui ) {
                    prelim_prep_instruction = $(this).text();
                  }
              }
              );
              var dynamic_div_drop = $(document.createElement('div')).css({
                border: '1px dashed', position: 'relative',
                width: 'max-content', height: 'max-content', padding: '3', margin: '0'
              });
              $(dynamic_div_drop).append("<input type='text' name='prep" +iCnt+"'"+">");
              $(dynamic_div_drop).appendTo('#divContainer-drop')
              $("input").droppable(
                {
                  activeClass: "active",
                  hoverClass:  "hover",
                  drop :function(event, ui) {
                    $( this ).addClass( "ui-state-highlight" );
                    $( this ).addClass( "ui-widget-header" );
                    $( this ).val(prelim_prep_instruction);
                  }
                
                } );
              $(order_prep).append("<p>"+iCnt+"</p>");
              iCnt = iCnt + 1;
            }
            
            //Execution
            input_value_execution = $('#holder-input-execution').val();
            if (input_value_execution !=''){
              $(dynamic_div2).append("<li >"+input_value_execution+"</li>");
              $(dynamic_div2).text()
              $('#holder-input-execution').val("");
            // Append the newly created DIV to the container.
              $(dynamic_div2).appendTo('#divContainer2').draggable(
                {
                  cursor: "move",
                  drag: function( event, ui ) {
                    prelim_exec_instruction = $(this).text();
                  }
              }
              );
              var dynamic_div_drop2 = $(document.createElement('div')).css({
                border: '1px dashed', position: 'relative',
                width: 'max-content', height: 'max-content', padding: '3', margin: '0'
              });
              $(dynamic_div_drop2).append("<input type='text' name='execution" +iCnt2+"'"+">");
              $(dynamic_div_drop2).appendTo('#divContainer-drop2')
              $("input").droppable(
                {
                  activeClass: "active",
                  hoverClass:  "hover",
                  drop :function(event, ui) {
                    $( this ).addClass( "ui-state-highlight" );
                    $( this ).addClass( "ui-widget-header" );
                    $( this ).val(prelim_exec_instruction);
                  }
                
                } );
              $(order_exec).append("<p>"+iCnt2+"</p>");
              iCnt2 = iCnt2 + 1;
            }
            
            }
          });
        })
});

