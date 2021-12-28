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
    $("#outer-grid").hover(function(){
        counter = counter + 1;
        // window.alert(counter)
        // counting = "<div class= 'form-group'>" + "<input type='text' name='execution"+counter2+"'"+"  id = 'execution_element'>"+counter+"</div>"
        $(".Order-Prep").append("<div class= 'form-group'><h3><label for ='hold'>"+counter+"</label><input type='text' style='display:none' name='hold'></h3></div>");
        $(".Landing-Prep").append("<div class= 'form-group'><h3><input type='text' name='prep" +counter+"'"+"></h3></div>");
        $(".Order-Execution").append("<div class= 'form-group'><h3><label for ='execution"+ counter+"'>"+counter+"</label><input type='text' style='display:none' name='execution" +counter+"'"+"></h3></div>");
        $(".Landing-Execution").append("<div class = 'form-group'><h2/></div>")
        

        // window.alert('ya')
    });
    // jQuery methods go here...
    // $("#inner-grid").droppable()
});

