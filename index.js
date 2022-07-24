
function sleep(ms, msg) {
    console.log(`Sleeping for ${ms}ms - ${msg}`)
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
    let all_inputs_valid = true;
    for (const prop in inputs) {
        if (inputs[prop] === "undefined" || inputs[prop] === 0) { //HTML is sending back a string
            all_inputs_valid = false;
            break;
        }
    }
    if (!all_inputs_valid) {
        console.log("Attempted to play without checking all settings.");
        document.getElementById('incomplete_warning').style.display = "block";
        return;
    }
    document.getElementById('incomplete_warning').style.display = "none"; //Remove error msg before continuing

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

    the_game(op, ed, inputs['rounds'], inputs['countdown']);
}

async function the_game(op, ed, rounds, countdown) {
    const all_data = await getJsonFile('oped_anime_data');
    let used_vids = [];
    let picked = undefined;

    document.getElementById("the_game").style.display = "block";

    let i, tabcontent;
    tabcontent = document.getElementsByClassName("tabcontent");
      for (i = 0; i < tabcontent.length; i++) {
            tabcontent[i].style.display = "none";
    }
    tabcontent = document.getElementsByClassName("tab");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }

    //Main Rounds Loop
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
            //TODO Doesn't switch back visuals before returning...
            return;
        }

        const vid_url = `https://v.animethemes.moe/${picked.vid_source}.webm`;
        console.log(`Going to play ${picked.name_of_vid} from ${picked.show_name}  --  ${vid_url}`);

        //Get the new source
        const display_video_max_frames = 30 * countdown; //Usually ten seconds
        let now_showing_vid = false; //Turns on canvas drawing during a second 'play()'


        let canvas = document.getElementById('the_canvas');
        let ctx = canvas.getContext('2d');
        let video = document.getElementById('video');
        let source = document.createElement('source');
        source.setAttribute('src', vid_url);
        video.appendChild(source);

        try {
            //video.load();
            video.play();
        } catch (err) {
            console.log(err)
        }

        video.volume = 1.0;

        //Buffering delay
        ctx.fillStyle = 'dimgrey';
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.textAlign = 'center';
        ctx.fillStyle = 'skyblue';
        ctx.font = "60px Arial";
        while (video.buffered.length === 0) {
            ctx.fillText("Buffering...", 512, 288);
            await sleep(100, 'Buffering');
        }
        console.log("Buffered!");


        //Countdown
        for (let sec = 0; sec < countdown*100; sec++) {
            if (sec === 0) console.log("Starting Countdown");
            ctx.fillStyle = 'dimgrey';
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            ctx.fillStyle = 'skyblue';
            ctx.font = "normal 120px Arial";
            ctx.fillText((Math.floor((countdown*100-sec)/100)+1).toString(), 512, 288);
            ctx.font = "italic 50px Arial";
            ctx.fillText(`#${i+1}`, 75, 75);

            let grd = ctx.createLinearGradient(1024, 576, 0, 0);
            grd.addColorStop(0, "skyblue");
            grd.addColorStop(1, "dimgrey");
            ctx.fillStyle = grd;
            ctx.fillRect(0, 500, 1024 - Math.floor(1024 * (sec/(countdown*100))), 76);
            await sleep(10, 'Drawing countdown');
        }
        now_showing_vid = true;
        video.pause();
        await sleep(1, 'Pause buffer'); //You need another pause to reactivate play
        video.play();

        // Prepare info for canvas/paragraphs
        let this_show_name = picked.show_name + ` - ${picked.type_of_vid === 'op' ? 'Opening' : 'Ending'}`; //Must be a 'var'
        let aka = picked.alt_names.length !== 0 ? picked.alt_names.join(', ') : '';
        let this_series = picked.series !== 'NA' ? `${picked.series}` : '';
        let used = picked.vid_episodes === '---' ? `This ${picked.type_of_vid === 'op' ? 'OP' : 'ED'} used in episode(s) '${picked.vid_episodes}'` : '';

        const show_name_font = this_show_name.length > 50 ? 25 : 40; //40px by default

        let show_info = ''; //`<b>Anime: </b>${this_show_name}`; //Already introduced the show
        if (aka !== '') show_info += `<li><b>Alternate Titles: </b>${aka}</li>`;
        show_info += `<li><b>Song: </b>${picked.name_of_vid}</li>`;
        if (this_series !== '') show_info += `<li><b>Series: </b>${this_series}</li>`
        if (used !== used) show_info += `<li>${used}</li>`
        document.getElementById('show_info').innerHTML = show_info;
        document.getElementById('synopsis').innerHTML = `<b>Synopsis:</b> ${picked.synopsis}`;

        //Displaying Results - Show video with name
        for (let cntr = 0; cntr < display_video_max_frames; cntr++) {
            ctx.drawImage(video, 0, 0, 1024, 576);

            ctx.fillStyle = '#696969'; //dimgrey
            ctx.strokeStyle = '#87CEEB'; //skyblue
            ctx.lineWidth = 8;
            ctx.beginPath();
            ctx.moveTo(0, 516); //1
            ctx.lineTo(1024, 516); //2
            ctx.stroke();
            ctx.lineTo(1024, 576); //3
            ctx.lineTo(0, 576); //4 - lowest left
            ctx.closePath();
            ctx.fill();

            //Display Title
            ctx.strokeStyle = '#1e90ff'; //dodgerblue
            ctx.lineWidth = 5
            ctx.fillStyle = '#fff';
            ctx.font = `${show_name_font}px Verdana`; //${Math.floor(this_show_name.length / 60)}
            ctx.strokeText(this_show_name, 512, 558);
            ctx.fillText(this_show_name, 512, 558);

            //Fade out
            if (cntr > display_video_max_frames - 30 && video.volume > 0.05) video.volume -= 0.05;
            //Note: if the argument is 'video.volume > 0', it will cause issues
            await sleep(100/3,'Displaying results') //Draw at 30 FPS
        }

        console.log("You've reached the end!")


        //Clean up for next round
        picked = undefined;
        document.getElementById('show_info').innerHTML = '';
        document.getElementById('synopsis').innerHTML = '';
        ctx.fillStyle = 'skyblue';
        ctx.font = "60px Arial";
        video.pause();

        source.remove();
    }


    //Reset and Go Back to Default
    document.getElementById("oped_game").style.display = "block";
    tabcontent = document.getElementsByClassName("tab");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "block";
    }
    document.getElementById("the_game").style.display = "none";
}