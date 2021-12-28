// $(function(){
//     $("#instruction_raw").draggable()
//     // jQuery methods go here...
// });

$(function(){
    var counter = 0;
    $("#inst_button").click(function(){
        // e.preventDefault()
        
        value = $("#input-holder").val()
        // new_input = "<div class='input-area'>" + label + input + button +"</div>"
        new_input = "<li>" + value +"</li>"
        $("#instruction_raw").append(new_input);
        $("li").draggable()
        // console.log(counter)
       
        // window.alert("huh")
      });
    $(".holder").hover(function(){
        counter = counter + 1;
        // window.alert(counter)
        counting = "<p>" + counter +"</p>"
        $(".holder2").append(counting);
        // window.alert('ya')
    });
    // jQuery methods go here...
    // $("#inner-grid").droppable()
});

