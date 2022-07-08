

function start() {
    let inputs = {
        "type_of_vid": document.querySelector('#opening_ending').value, //OP, ED, or both
        "rounds": parseInt(document.querySelector('#rounds').value),
        "countdown": parseInt(document.querySelector('#countdown').value)
    }
    console.log(Object.values(inputs));

    //Check that all values are entered/not 'undefined'
    if (!Object.values(inputs).every(value => value)) {
        document.getElementById('incomplete_warning').display = 'block';
        return;
    }
    document.getElementById('incomplete_warning').display = 'none'; //Remove error msg

    let game_data;
    //console.log(Object.getOwnPropertyNames(all_data))

    switch(inputs['type_of_vid']) {
        case 'op':
            game_data = all_data['openings'];
            break;
        case 'ed':
            game_data = all_data['endings'];
            break;
        case 'both':
            game_data = all_data['openings'].concat(all_data['endings'])
            break;
    }

    // game_data = game_data.filter(function (currentElement) {
    //     return currentElement.includes("i"); //Example
    //     // TODO Go through each vid searching for requirements
    // });

    console.log(game_data);
}


function the_game(game_data) {

}





function openCity(evt, game_type) {
  // Declare all variables
  var i, tabcontent, tablinks;

  // Get all elements with class="tabcontent" and hide them
  tabcontent = document.getElementsByClassName("tabcontent");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }

  // Get all elements with class="tablinks" and remove the class "active"
  tablinks = document.getElementsByClassName("tablinks");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" active", "");
  }

  // Show the current tab, and add an "active" class to the button that opened the tab
  document.getElementById(game_type).style.display = "block";
  evt.currentTarget.className += " active";
}
document.getElementById("default_game_tab").click(); //Default Open</script>
