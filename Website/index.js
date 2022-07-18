
async function getJsonFile(file_name) {
    if (!file_name.endsWith('.json'))
        file_name += '.json';
    console.log(`Getting file '${file_name}'`);
    let file_location = `http://127.0.0.1:8887/${file_name}`;

    const data = await fetch(file_location, {
        method: 'GET',
        mode: 'no-cors',
        cache: 'default',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Access-Control-Allow-Origin': '*'
          }
        })
    .then(response => console.log(response))
    .then(data => console.log(data))
    .then(text => console.log(text));
}

getJsonFile('oped_anime_data');


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

