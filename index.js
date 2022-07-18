async function getJsonFile(file_name) {
    if (!file_name.endsWith('.json'))
        file_name += '.json';
    file_name = `./Data/${file_name}`
    console.log(`Getting file '${file_name}'`);
    return await fetch(file_name)
        .then(response => {
            return response.json();
        })
        .then(data => console.log(data));
}


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

    let op = false;
    let ed = false;
    switch(inputs['type_of_vid']) {
        case 'op':
            op = true;
            break;
        case 'ed':
            ed = true;
            break;
        case 'both':
            op = true;
            ed = true;
            break;
    }

    the_game(op, ed, inputs['rounds'], inputs['countdown'])
}

function the_game(op, ed, rounds, countdown) {
    const all_data = getJsonFile('oped_anime_data');
    console.log(all_data);
    let used_vids = [];
    let picked = undefined;
    let vid_choices = [];

    console.log("Hiding 'tabcontents' classes");
    let i, tabcontent;
    tabcontent = document.getElementsByClassName("tabcontent");
      for (i = 0; i < tabcontent.length; i++) {
            tabcontent[i].style.display = "none";
    }
    tabcontent = document.getElementsByClassName("tab");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }


    for (let i = 0; i < rounds; i++) {
        //Pick a video
        let cannot_find_a_video = 0;  //Stop it from getting stuck in a loop
        while (picked === undefined) {
            let keys = Object.keys(all_data);
            console.log(keys);
            let random_show = all_data[keys[Math.floor(Math.random()*keys.length)]];
            console.log(`Random show '${random_show}'`);

            function addToChoices(op_or_ed) {
                for (let x in Object.keys(all_data[random_show][op_or_ed])) {
                    let vid_epi = Object.keys(all_data[random_show][op_or_ed][x])[0];
                    let vid_src = all_data[random_show][op_or_ed][x];
                    vid_choices.push({
                        show_name: random_show,
                        alt_names: all_data[random_show]['alt titles'],
                        type_of_vid: op_or_ed,
                        name_of_vid: x,
                        vid_episodes: vid_epi,
                        vid_source: vid_src
                    });
                }
                console.log(vid_choices)
            }
            if (op && all_data[random_show].op.length !== 0) {
                addToChoices('op');
            }
            if (ed && all_data[random_show].ed.length !== 0) {
                addToChoices('ed');
            }

            //Pick from choices. Make sure it's a new one too.
            if (vid_choices.length !== 0) {
                picked = vid_choices[Math.floor(Math.random()*vid_choices.length)];
                if (!used_vids.includes(picked.name_of_vid)) {
                    used_vids.push(picked.name_of_vid);
                } else {
                    picked = undefined;
                    continue;
                }
            }

            if (cannot_find_a_video > 10)
                break;
            else
                cannot_find_a_video++;
        }
        if (cannot_find_a_video > 10) {
            console.log("ERROR - Did too many loops while trying to find an appropriate video.");
            return;
        }


        //Present the picked video
        vid_choices = [];
    }


    //Reset and return to menu
    document.getElementById("oped_game").style.display = "block";
    tabcontent = document.getElementsByClassName("tab");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "block";
    }


}