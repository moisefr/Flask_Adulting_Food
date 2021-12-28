// $(function(){
//     $("#instruction_raw").draggable()
//     // jQuery methods go here...
// });

$(function(){
    $("#inst_button").click(function(){
        // e.preventDefault()
        value = $("#input-holder").val()
        console.log(value)
        // new_input = "<div class='input-area'>" + label + input + button +"</div>"
        new_input = "<li>" + value +"</li>"
        $("#instruction_raw").append(new_input);
        $("li").draggable()
        // window.alert("huh")
      });
    // jQuery methods go here...
});

