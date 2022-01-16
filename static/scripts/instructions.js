$(function(){
    var counter = 0;
    var prelim_instruction;
    // window.onload($(function(){
    //     $("#instruction_raw").prepend("Drag Each List Item in order of instruction");
    // }))
    // Insturction Generator
    $("#inst_button").click(function(e){
        value = $("#input-holder").val()
        new_input = "<li id ='prelim_instruction'>" + value +"</li>"
        $("#instruction_raw").append(new_input);
        // Draggable Instructions
        $("li").draggable({
            cursor: "move",
            drag: function( event, ui ) {
                prelim_instruction = $(this).text();
                $(this).css({
                    "background-color": "yellow", 
                    "font-size": "125%",
                    "list-style-type": "none",
                    "width": "10%",
                    "height":" 35px"
                });
             }
        });
        e.preventDefault()
      });
    //  Form Landing Sites
    $("#outer-grid").hover(function(){
        counter = counter + 1;
        $(".Order-Prep").append("<div class= 'form-group'><h2><label for ='hold'>"+counter+"</label><input type='text' style='display:none' name='hold'></h2></div>");
        $(".Landing-Prep").append("<div class= 'form-group'><h4><input style='font-size:x-large' type='text' name='prep" +counter+"'"+"></h4></div>");
        $(".Order-Execution").append("<div class= 'form-group'><h2><label for ='hold'>"+counter+"</label><input type='text' style='display:none' name='hold'></h2></div>");
        $(".Landing-Execution").append("<div class= 'form-group'><h4><input  type='text' style='font-size:x-large' name='execution" +counter+"'"+"></h4></div>");
        $("input").droppable({
            activeClass: "active",
            hoverClass:  "hover",
            drop: function( event, ui ) {
               $( this ).addClass( "ui-state-highlight" );
               $( this ).addClass( "ui-widget-header" );
               $( this ).val(prelim_instruction);
            }
         });
    });
    var submit = document.getElementById('submit');
    var form = document.getElementByName('updates');
    $(submit).click(function(e){
        $(form).submit()
    })
    // jQuery methods go here...
    // $("#inner-grid").droppable()
});

