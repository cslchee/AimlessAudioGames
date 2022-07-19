function sleep(ms) {
    console.log(`Sleeping for ${ms}ms`)
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function getJsonFile(file_name) {
    if (!file_name.endsWith('.json'))
        file_name += '.json';
    file_name = `./Data/${file_name}`
    console.log(`Getting file '${file_name}'`);
    const temp = await fetch(file_name)
        .then(response => {
            return response.json();
        })
        .then(data => {
            console.log(data);
            return data;
        });
    return temp;
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

async function the_game(op, ed, rounds, countdown) {
    const all_data = await getJsonFile('oped_anime_data');
    console.log(all_data);
    let used_vids = [];
    let picked = undefined;

    console.log("Hiding 'tabcontents' classes...");
    let i, tabcontent;
    tabcontent = document.getElementsByClassName("tabcontent");
      for (i = 0; i < tabcontent.length; i++) {
            tabcontent[i].style.display = "none";
    }
    tabcontent = document.getElementsByClassName("tab");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }

    //Main Countdown Loop
    for (let i = 0; i < rounds; i++) {
        //Pick a video
        let cannot_find_a_video = 0;  //Stop it from getting stuck in a loop
        while (picked === undefined) {
            let keys = Object.keys(all_data);
            let vid_choices = [];
            let random_show = keys[Math.floor(Math.random()*keys.length)];
            console.log(`Random show '${random_show}'`);

            function addToChoices(op_or_ed) {
                const all_vids = Object.keys(all_data[random_show][op_or_ed]);
                for (let v = 0; v < all_vids.length; v++) {
                    let vid_epi = Object.keys(all_data[random_show][op_or_ed][all_vids[v]])[0];
                    let vid_src = all_data[random_show][op_or_ed][all_vids[v]][vid_epi];
                    vid_choices.push({
                        show_name: random_show,
                        alt_names: all_data[random_show]['alt titles'],
                        series: all_data[random_show]['series'],
                        synopsis: all_data[random_show]['synopsis'],
                        type_of_vid: op_or_ed,
                        name_of_vid: all_vids[v],
                        vid_episodes: vid_epi,
                        vid_source: vid_src
                    });
                }
                console.log(vid_choices);
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
        console.log(`Going to play ${picked.name_of_vid} from ${picked.show_name}`);


        //Display Countdown and play audio
        document.getElementById("the_game").style.display = "block";
        document.getElementById("name_type_and_series").innerHTML = "";
        document.getElementById("synopsis").innerHTML = "";

        let the_canvas = document.getElementById('the_canvas');
        let ctx = the_canvas.getContext('2d');
        ctx.font = '80px Arial';


        //PLAY THE MUSIC
        var ent_video = document.querySelector('video');
        ent_video.addEventListener('')
        let the_video = document.getElementById("the_video");
        the_video.style.display = "none"; //hide video

        the_video.play();



        for (let sec = 0; sec < countdown*100; sec++) {
            //Redraw Background
            ctx.fillStyle = 'dimgrey';
            ctx.clearRect(0, 0, the_canvas.width, the_canvas.height);

            ctx.fillStyle = 'skyblue';
            ctx.fillText((Math.floor((countdown*100-sec)/100)+1).toString(), 360, 240);

            let grd = ctx.createLinearGradient(720, 480, 0, 0);
            grd.addColorStop(0, "skyblue");
            grd.addColorStop(1, "dimgrey");
            ctx.fillStyle = grd;
            ctx.fillRect(0, 440, 720 - Math.floor(720 * (sec/(countdown*100))), 40);
            await sleep(10);
        }


        //Display Result
        let ntas = `<b>${picked.show_name}</b>`;
        if (op !== ed) //Only use for both
            ntas += ` (${picked.type_of_vid === 'op' ? 'Opening' : 'Ending'})`;
        if (picked.alt_names.length !== 0)
            ntas += `<br>&emsp;<i>aka ${picked.alt_names.join(', ')}</i>`;
        if (picked.series !== 'NA')
            ntas += `<br>Series: ${picked.series}`;
        ntas += `<br>Used in episode(s) '${picked.vid_episodes}'`;
        document.getElementById("name_type_and_series").innerHTML = ntas;
        document.getElementById("synopsis").innerHTML = picked.synopsis;


        for (let sec = 0; sec < countdown; sec++ ) {

        }










        picked = undefined;
    }


    //Reset and Go Back to Default
    document.getElementById("oped_game").style.display = "block";
    tabcontent = document.getElementsByClassName("tab");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "block";
    }
    document.getElementById("the_game").style.display = "none";

}