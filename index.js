let real_vgm_data = {} // Global needed for asynchronous usage
let reveal_msg = ""

function titleCase(str) {
    str = str.toLowerCase().split(' ');
    for (var i = 0; i < str.length; i++) {
    str[i] = str[i].charAt(0).toUpperCase() + str[i].slice(1);
    }
    return str.join(' ');
}

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
    //Collect loads of HTML data here to simplify code later
    let inputs = {
        "type_of_vid": document.querySelector('#opening_ending').value, //OP, ED, or both
        "rounds": !isNaN(parseInt(document.querySelector('#rounds').value)) ? parseInt(document.querySelector('#rounds').value) : "undefined",
        "countdown": parseInt(document.querySelector('#countdown').value),
        "include_movies": document.querySelector('#include_movies').value === 'yes',
        "premiered_after": document.querySelector('#premiered_after').value, //Just the year
        "rankings": document.querySelector('#rankings').value,
        "start_point_random": document.querySelector('#start_point_random').value === 'random_point',
        "cas_bias": document.getElementById('cas_bias').checked,
        "genre_is_all": document.getElementById('pick_genres').value === 'all'
    }
    console.log(Object.values(inputs));

    //Check for custom rounds value
    if (document.querySelector('#rounds').value === 'Custom' && inputs.rounds === "undefined") {
        console.log("Validating Custom Rounds Entry")
        const custom_rounds_val = parseInt(document.querySelector('#custom_rounds').value)
        console.log(custom_rounds_val)
        if (!isNaN(custom_rounds_val) && custom_rounds_val > 1 && custom_rounds_val < 1000) {
            inputs.rounds = custom_rounds_val;
        } else {
            document.getElementById('custom_rounds_error_msg').style.display = 'block';
        }
    }

    //Check for custom genre choices
    let genres_to_remove = [];
    if (!inputs['genre_is_all']) {
        const collection = document.getElementsByClassName('genre_checkboxes');
        for (let i = 0; i < collection.length; i++) {
            if (collection[i].checked === false) {
                const temp = titleCase(collection[i].id.replace('genre_','').replace(' ','_'))
                genres_to_remove.push(temp);
            }
        }
        console.log(`Removing genres: ${genres_to_remove}`);
    }
    console.log(genres_to_remove.length)
    if (!inputs['genre_is_all'] && genres_to_remove.length === 0) {
        document.getElementById('general_warnings').innerHTML = `Please pick "All" from the dropdown list if you're not going to exclude any genres.`;
        document.getElementById('general_warnings').style.display = 'block';
        return;
    } else if (genres_to_remove.length > 14) { //Don't get too small - also avoid 'ecchi-only'
        document.getElementById('general_warnings').innerHTML = 'Must have at least 4 genres selected to continue.';
        document.getElementById('general_warnings').style.display = 'block';
        return;
    }

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
    //Remove error messages before continuing
    document.getElementById('incomplete_warning').style.display = "none";
    document.getElementById('custom_rounds_error_msg').style.display = "none";
    document.getElementById('general_warnings').style.display = 'none';
    document.getElementById('general_warnings').innerHTML = '';



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

    the_game(op, ed, inputs['rounds'], inputs['countdown'], inputs['include_movies'], inputs['premiered_after'],
        inputs['rankings'], inputs['start_point_random'], inputs['cas_bias'], genres_to_remove); // TODO Clean this up. Just sent over inputs plz
}

async function filtration(include_movies, premiered_after, rankings, genres_to_remove) { //Leaves op/ed handling to 'the_game'
    console.log("Filtering Data...");
    const all_data = await getJsonFile('oped_anime_data');
    let real_data = JSON.parse(JSON.stringify(all_data)); //Deep copy - Doing this subtractively. Few operations. Easier syntax.

    const rankings_data = rankings === 'everything' ? [] : await getJsonFile('top_data.json');
    const rankings_on = rankings_data.length !== 0; //simplified check for reuse later
    let rankings_valid_shows = [];
    if (rankings_on){
        const rank_term = rankings.includes('pop') ? 'popular' : 'rating';
        const top_num_term = rankings.replace(rank_term,'') //gives 'top50', etc.

        //Always include top50
        rankings_valid_shows = rankings_data[rank_term]['top50'];
        if (top_num_term.includes('100') || top_num_term.includes('250')) {
            rankings_valid_shows = rankings_valid_shows.concat(rankings_data[rank_term]['top100']);
        }
        if (top_num_term.includes('250')) {
            rankings_valid_shows = rankings_valid_shows.concat(rankings_data[rank_term]['top250']);
        }
    }


    let del_flag;
    for (let anime in all_data) {
        del_flag = false;
        if (!del_flag && rankings_on && !rankings_valid_shows.includes(anime)) { del_flag = true; }
        if (!include_movies && anime.toLowerCase().includes('movie')) { del_flag = true; }
        if (!del_flag && premiered_after !== 'NA') {
            let min_date = parseInt(premiered_after);
            let this_date = parseInt(all_data[anime].date.split(' ')[1]);
            if (this_date < min_date) { del_flag = true; } //Could make <=, sticking with 'after' for now though
        }
        if (!del_flag && genres_to_remove) {
            const animes_genres = all_data[anime]['genres']
            //Delete any 'genre-less' animes to avoid mix-ups
            if (animes_genres.length === 0) {
                del_flag = true; //Removes 287
            } else {
                //Delete this anime if it includes a genre that's being removed
                for (const g of genres_to_remove) {
                    if (animes_genres.includes(g)) {
                        del_flag = true;
                        break;
                    }
                }
            }
        }


        if (del_flag) { delete real_data[anime]; }
    }


    return real_data;
}

async function the_game(op, ed, rounds, countdown, include_movies, premiered_after, rankings,
                        start_point_random, cas_bias, genres_to_remove) {
    const all_data = await filtration(include_movies, premiered_after, rankings, genres_to_remove);
    let cas_bias_data = cas_bias ? await getJsonFile('top_data') : [];
    if (cas_bias) {cas_bias_data = cas_bias_data['cas_bias']}

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
            //Cas Bias
            if (Math.floor(Math.random() * 100) === 69) { //Small chance to get one I know
                console.log("Doing a biased show for Cas~~~~~~~");
                random_show = cas_bias_data[Math.floor(Math.random()*cas_bias_data.length)];
            }

            //console.log(`Random show '${random_show}'`); //Spoiler

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
                        premiere_of_vid: all_data[random_show]['date'],
                        type_of_vid: op_or_ed,
                        name_of_vid: all_vids[v],
                        anilist_genres: all_data[random_show]['genres'],
                        vid_episodes: vid_epi,
                        vid_source: vid_src
                    });
                }
                //console.log(vid_choices);
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
            //Switch back visuals before returning...
            document.getElementById("oped_game_menu").style.display = "block";
            tabcontent = document.getElementsByClassName("tab");
            for (i = 0; i < tabcontent.length; i++) { tabcontent[i].style.display = "block"; }
            document.getElementById("the_game").style.display = "none";
            return;
        }

        const vid_url = `https://v.animethemes.moe/${picked.vid_source}.webm`;
        //console.log(`Going to play ${picked.name_of_vid} from ${picked.show_name}  --  ${vid_url}`); //Spoilers

        //Get the new source
        const display_video_max_frames = 30 * countdown; //Usually ten seconds


        let canvas = document.getElementById('the_canvas');
        let ctx = canvas.getContext('2d');
        let video = document.getElementById('video');
        let source = document.createElement('source');
        source.removeAttribute('src'); video.load(); //Empty Source before getting new one
        source.setAttribute('src', vid_url);
        video.appendChild(source);

        video.play();
        video.volume = 1.0;

        //Buffering delay
        ctx.fillStyle = 'dimgrey';
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.textAlign = 'center';
        ctx.fillStyle = 'skyblue';
        ctx.font = "60px Arial";
        ctx.fillText("Buffering...", 512, 288);
        while (video.buffered.length === 0) {
            await sleep(50, 'Buffering');
        }
        console.log("Buffered!");


        //TODO Sync video timecode loading with timecode change
        if (start_point_random) { //Do after buffering to avoid 'video.duration' as NaN
            // video.addEventListener('loadeddata', function() {
            //     console.log("Can play data 'loadeddata'");
            //     console.log(this.currentTime);
            // }, false);
            video.currentTime = Math.random() * (video.duration - 30); //Don't get within 30sec of the end. Round to 2nd place
            await sleep(500, 'Waiting a bonus second for random time update');
        }


        //Countdown
        for (let sec = 0; sec < countdown*1000; sec += 25) { //Use a 'time.now()' difference while-loop instead?
            if (sec === 0) console.log("Starting Countdown");
            ctx.fillStyle = 'dimgrey';
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            ctx.fillStyle = 'skyblue';
            ctx.font = "normal 120px Arial";
            ctx.fillText((Math.floor((countdown*1000-sec)/1000)+1).toString(), 512, 288);
            ctx.font = "italic 50px Arial";
            ctx.fillText(`#${i+1}`, 75, 75);

            let grd = ctx.createLinearGradient(1024, 576, 0, 0);
            grd.addColorStop(0, "skyblue");
            grd.addColorStop(1, "dimgrey");
            ctx.fillStyle = grd;
            ctx.fillRect(0, 500, 1024 - Math.floor(1024 * (sec/(countdown*1000))), 76); //Countdown bar
            ctx.fillRect(0, 0, Math.floor(1024 * ((rounds-i)/rounds)), 20); //Progress bar
            video.volume = document.getElementById("myRange").value / 100;
            await sleep(25, 'Drawing countdown');
        }

        // Prepare info for canvas/paragraphs
        let this_show_name = picked.show_name;
        if (op && ed) this_show_name += ` - ${picked.type_of_vid === 'op' ? 'Opening' : 'Ending'}`; //Display which it is if we're doing both
        let aka = picked.alt_names.length !== 0 ? picked.alt_names.join(', ') : '';
        let this_series = picked.series !== 'NA' ? `${picked.series}` : '';
        let used = picked.vid_episodes === '---' ? `This ${picked.type_of_vid === 'op' ? 'OP' : 'ED'} used in episode(s) '${picked.vid_episodes}'` : '';
        let anilist_genres = picked.anilist_genres.length !== 0 ? picked.anilist_genres.join(', '): '';

        const show_name_font = this_show_name.length > 50 ? 25 : 40; //40px by default

        let show_info = ''; //`<b>Anime: </b>${this_show_name}`; //Already introduced the show
        if (aka !== '') show_info += `<li><b>Alternate Titles: </b>${aka}</li>`;
        show_info += `<li><b>Song: </b>${picked.name_of_vid}</li>`;
        show_info += `<li><b>Premiered: </b>${picked.premiere_of_vid}</li>`;
        if (this_series !== '') show_info += `<li><b>Series: </b>${this_series}</li>`;
        if (anilist_genres !== '') show_info += `<li><b>Genres:</b> ${anilist_genres}</li>`;
        if (used !== used) show_info += `<li>${used}</li>`;
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

            //Volume
            let fade_out_percent = (cntr >= display_video_max_frames - 30 && video.volume > 0.001) ? (display_video_max_frames - cntr) / 30 : 1;
            video.volume = (document.getElementById("myRange").value / 100) * fade_out_percent;
            //console.log("Video Volume:", video.volume, "\tSlider Volume:", document.getElementById("myRange").value, "\tPercentage:", (display_video_max_frames - cntr) / 30);

            await sleep(100/3,'Displaying results'); //Draw at 30 FPS
        }

        console.log("You've reached the end!");


        //Clean up for next round
        picked = undefined;
        document.getElementById('show_info').innerHTML = '';
        document.getElementById('synopsis').innerHTML = '';
        ctx.fillStyle = 'skyblue';
        ctx.font = "60px Arial";
        video.pause();
        source.remove();
        if (i === rounds) { source.removeAttribute('src'); video.load(); } //Can't play afterwards (could hit keyboard |> key)
    }


    //Reset and Go Back to Default
    document.getElementById("oped_game_menu").style.display = "block";
    tabcontent = document.getElementsByClassName("tab");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "block";
    }
    document.getElementById("the_game").style.display = "none";
}

async function start_steam_game() {
    let steam_id = document.getElementById('steam_id').value;
    //Input validation
    let steam_warning = document.getElementById('steam_general_warnings');
    if (steam_id.length !== 17) {
        steam_warning.innerHTML = "Please make sure that your Steam ID is exactly 17 digits long.";
        steam_warning.style.display = 'block';
        return;
    } else if (steam_id.length === 0) {
        steam_warning.innerHTML = "Dude, enter a number please.";
        steam_warning.style.display = 'block';
    }
    if (isNaN(parseInt(steam_id))) {
        steam_warning.innerHTML = "Your input was not a number.";
        steam_warning.style.display = 'block';
        return; 
    } else if (parseInt(steam_id) <= 0) {
        steam_warning.innerHTML = "Why would you even put a negative number in here dude?";
        steam_warning.style.display = 'block';
        return;
    }
    steam_warning.innerHTML = '';
    steam_warning.style.display = 'none';

    console.log(`Given steam profile: https://steamcommunity.com/profiles/${steam_id}`)

    const API_KEY = ""; // It's a secret ;)
    const game_page = `http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key=${API_KEY}&steamid=${steam_id}&format=json`;

    //Get games and playtimes from Value
    // const temp = await fetch(game_page, {
    //     mode: 'cors',
    //     headers: {
    //         'Access-Control-Allow-Origin': '*' //or 'http://api.steampowered.com'???
    //     }
    // })
    // .then(response => {console.log(response);})
    // .then(data => {console.log(data); return data;})
    // .catch(error => {console.log('Request failed', error)});

    //const user_ids_pts = temp['response']['games'];
    console.log(temp);

    //TODO https://stackoverflow.com/questions/35861871/steam-api-access-control-allow-origin-issue
}

// --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --

async function start_vgm_game() {
    console.log("Starting VGM Game!")
    const all_data = await getJsonFile('khi_data');
    let invalid_request = false
    real_vgm_data = {} //Clear object

    let player_choice = document.getElementById('sort_by').value
    switch(player_choice) {
        case "popularity":
            console.log("Sorting by Popularity");
            let category_data = await getJsonFile('khi_categories')
            const category_type = document.querySelector('#popularity_options').value

            if (category_type === 'literally_everything') {
                real_vgm_data = JSON.parse(JSON.stringify(all_data)); //Deep copy
                break; // Leave switch
            }

            category_data = category_data[category_type] //Get sub-list we need to sort out of
            for (const album of category_data) {
                let selection = all_data[album]
                if (selection !== undefined) {  // Skip the missing ones
                    real_vgm_data[album] = selection
                }
            }
            break;
        case "consoles":
            console.log("Sorting by Consoles");
            let selected_consoles = []
            const console_collection = document.getElementsByClassName('console_checkboxes');
            for (const con of console_collection) {
                if (con.checked) {selected_consoles.push(con.value) }
            }
            // Given an empty list, display warning text and leave the function
            if (selected_consoles.length === 0) {
                invalid_request = true;
                console.log("Empty consoles list, cannot start");
                break;
            }

            console.log(`Searching for games on the: ${selected_consoles.join(', ')}`);

            let console_counter = 0;
            for (const album of Object.keys(all_data) ) {
                const album_consoles = all_data[album]['platforms']
                if (selected_consoles.some(element => album_consoles.includes(element))) {
                    real_vgm_data[album] = all_data[album];
                    console_counter += 1;
                }
            }
            console.log(`Found ${console_counter} viable albums for the console(s)`)
            break;
        case "franchises":
            console.log("Sorting by Franchises");

            const current_franchise = document.getElementById('franchises_options').value

            for (const album of Object.keys(all_data)) {
                if (album.toLowerCase().includes(current_franchise.toLowerCase())) {
                    real_vgm_data[album] = all_data[album];
                }
            }
            console.log(`Found ${real_vgm_data.length} games for '${current_franchise}'`);
            break;
        case "publishers":
            console.log("Sorting by Publishers");

            const publisher_selected = document.getElementById('publisher_options').value
            for (const album of Object.keys(all_data)) {
                let include_this_pub = false;
                const pub_list = all_data[album]['publisher'];
                if (pub_list.includes(publisher_selected)) {  // Easy detect, direct name included in pub list
                    include_this_pub = true;
                } else {    //Harder check, see if the value is a part of each of the publishers (i.e. 'Sony' vs 'Sony Records')
                    for (const individual_pub of pub_list){
                        if (individual_pub.toLowerCase().includes(publisher_selected.toLowerCase())) { // Is our selected publisher a substring?
                            include_this_pub = true;
                            break;
                        }
                    }
                }

                // Add if successful in either easy/hard search
                if (include_this_pub) {
                    real_vgm_data[album] = all_data[album];
                }
            }

            break;
        case "developers":
            console.log("Sorting by Developers");

            const dev_selected = document.getElementById('dev_options').value
            for (const album of Object.keys(all_data)) {
                const dev_list = all_data[album]['developer'];
                if (dev_list.includes(dev_selected)) {
                    real_vgm_data[album] = all_data[album];
                }
            }

            break;
        case "decades":
            console.log("Sorting by Decades");

            const decade = Number(document.getElementById('decade_options').value.replace('s',''))
            console.log(`Checking of the decade: ${decade}`)

            for (const album of Object.keys(all_data)) {
                let year = all_data[album]['year'];
                if (year !== "") {
                    year = Number(year);
                    if (year >= decade && year <= (decade+9)) {
                        real_vgm_data[album] = all_data[album];
                    }
                }
            }

            break;
    }
    if (invalid_request){
        document.getElementById("vgm_invalid_request").style.display = "block"
        return;
    }

    console.log(`Real VGM Data (Length ${real_vgm_data.length}):`)
    console.log(real_vgm_data)

    // Hide main DIVs and show game canvas
    let temp = document.getElementsByClassName("tabcontent");
    for (let i = 0; i < temp.length; i++) {
            temp[i].style.display = "none";
    }
    temp = document.getElementsByClassName("tab");
    for (i = 0; i < temp.length; i++) {
        temp[i].style.display = "none";
    }
    document.getElementById("the_vgm_game").style.display = "block";
    document.getElementById("vgm_invalid_request").style.display = "none"

    play_vgm_game()
}

async function play_vgm_game() {
    //Reset the display to a mystery
    const mystery_quotes = [
        "OwO What's dis?",
        "Is it just me or is it super annoying when people describe any music as \"a banger\"?",
        "The vibes of this one are making me feel feelings.",
        "Have ya heard this one before?",
        "There's something familiar about this tune...",
        "I swear I've heard this one before...",
        "I know exactly what this song is and I'm not tell you. :)",
        "Is this to your taste?",
        "My my, what a spectacular piece of music!",
        "This one is dead obvious. If you can't guess it, our relationship will never be the same.",
        "What could it be?",
        "New tune, who dis?",
        "I haven't a clue as to the origin of this particular tune.",
        "Tell me you’ve heard this before, or I’ll be shocked!",
        "Dang, this one is on the tip of my tongue/ear.",
        "Yawn, when is this thing gonna play something more obvious?",
        "Don't you hate it when you get an ambient noise track?",
        "Is this one a masterpiece or a piece of garbage?",
        "One thing I've learned after twenty-one years, you never known what's gonna walk through that door.",
        "I peeves me that 90% of this stuff isn't available for purchase or on streaming platforms.",
        "Man, who curates this database? Probably some nerd or something.",
        "Oh dude! I totally hate and or love the game this is from!",
        "Twenty bucks says the next song is City Escape.",
        "Tip: Don't do drugs.",
        "Hint: Press Ctrl+W",
        "Your free trial is about to expire in (2) songs. JK, imagine paying for access to internet content.",
        "Don't forget to drink water!",
        "Hmmm, I wonder what's for dinner...",
        "Deez notes! Heard 'em!",
        "I know the song, but I've never played the game it's from :/",
        "Psst, what's the name of the game this one is from?",
        "They should put this song in Beat Saber lmao",
        "What an iconic song.",
        "Such a signature sound, of course I know which game this is from.",
        "Don't know this tune? Well I must know your address because you must be living under a rock.",
        "I like this one :)",
        "Only real gamers know this jam.",
        "Whoop whoop, that's the sound of the police outside your door ready to interrogate you about whether or not you recognize this song.",
        "Ooof, I might not know this one.",
        "This soundtrack literally changed my life fr fr no cap.",
        "I was today years only when I heard this song for the first time.",
        "Could you imagine loosing your virginity to this song.",
        "Help! My ears are bleeding!",
        "Oops, almost for got to listen to this today."
    ]
    const buffering_quotes = [
        "Gimme a sec...",
        "Buffering...",
        "Digging through the archives...",
        "Finding your next song...",
        "Trying to find the AUX cable...",
        "Locating the next track...",
        "Loading new tune...",
        "Finding something tasty...",
        "Pausing to think..."
    ]
    let info_box = document.getElementById('album_info_box')
    info_box.textContent = buffering_quotes[Math.floor(Math.random() * buffering_quotes.length)]
    info_box.style.textAlign = 'center';
    let vgm_image =  document.getElementById('vgm_img')
    let question_block_image = document.getElementById("question_block_img")

    //Hide album cover to start, show a question block before reveal
    question_block_image.style.display = "block"
    vgm_image.style.display = "none"

    const vgm_button = document.getElementById("next_vgm_button");
    vgm_button.disabled = true;
    vgm_button.textContent = "Wait"

    const reveal_button = document.getElementById('vgm_reveal_button');
    reveal_button.disabled = true;
    reveal_button.textContent = "Please"

    //Get a random song
    const keys = Object.keys(real_vgm_data)
    const random_album_title = keys[Math.floor(Math.random() * keys.length)]
    const random_album = real_vgm_data[random_album_title]
    const album_thumbnail = `https://vgmsite.com/soundtracks/${random_album['album_url']}/${random_album['thumbnail']}`
    const alt_album_thumbnail = `https://kappa.vgmsite.com/soundtracks/${random_album['album_url']}/${random_album['thumbnail']}`

    const album_songs = Object.keys(random_album['songs'])
    const random_song_title = album_songs[Math.floor(Math.random() * album_songs.length)]
    const random_song_url = `https://kappa.vgmsite.com/soundtracks/${random_album['album_url']}/${random_album['songs'][random_song_title]}.mp3`

    //Preemptively load in the album cover
    vgm_image.src = album_thumbnail
    vgm_image.onerror = function() {
      console.log("Thumbnail failed to load. Loading alt thumbnail");
      vgm_image.src = alt_album_thumbnail;
    };

    //Add it to the src and play it at a random part
    console.log(`Cheat sheet\nNow playing ${random_album_title} - ${random_song_title}\nFrom ${random_song_url}`) //Cheat sheet
    const audio_player = document.getElementById('vgm_audio_player');
    let vgm_canvas = document.getElementById('vgm_canvas');
    let ctx = vgm_canvas.getContext('2d')
    audio_player.pause()
    audio_player.src = random_song_url
    audio_player.load();

    //Some constants for convenience
    const vgm_w = vgm_canvas.width
    const vgm_h = vgm_canvas.height

    //Buffer Audio and display notice
    ctx.fillStyle = 'dimgrey'
    ctx.clearRect(0,0, vgm_w, vgm_h); //Clear screen
    ctx.textAlign = 'center';
    ctx.fillStyle = 'skyblue';
    ctx.font = '60px sans-serif bold';
    ctx.fillText("Buffering...", vgm_w/2, vgm_h/2+3)

    let buffer_counter = 0
    while (audio_player.buffered.length === 0) {
        await sleep(100, 'Buffering');
        buffer_counter += 1
        if (buffer_counter > 200) {
            info_box.textContent = "Oops!\nWe might be stuck. Try refreshing the page..."
        }
    }
    const duration = audio_player.duration;
    console.log(`Duration: ${duration} seconds`);
    audio_player.currentTime = Math.random() * (duration - 20); // Choose a random starting point for the song

    //Play Audio
    console.log(`Playing VGM at time ${audio_player.currentTime}`)
    await audio_player.play();
    info_box.textContent = mystery_quotes[Math.floor(Math.random() * mystery_quotes.length)]

    //Countdown to reveals
    console.log("Starting Countdown");
    vgm_button.textContent = "Listen..."
    //Prep countdown bar
    let grd = ctx.createLinearGradient(vgm_w, vgm_h, 0, 0);
    grd.addColorStop(0, "skyblue");
    grd.addColorStop(1, "dimgrey");
    ctx.fillStyle = grd;

    const countdown = 10; // Must be an integer
    const speed = 25; //Lower a smoother countdown bar. Very smooth, but a little glitchy = 25, must fit cleanly into 1000
    let canceled_during_countdown = false;
    for (let sec = 0; sec < countdown*1000; sec += speed) { //Use a 'time.now()' difference while-loop instead?
        ctx.clearRect(0, 0, vgm_w, vgm_h);
        ctx.fillRect(0, 0, vgm_w - Math.floor(vgm_w * (sec/(countdown*1000))), vgm_h); //Countdown bar
        if (sec % 1000 === 0) {
            reveal_button.textContent = Math.round(countdown-(sec/1000)).toString() // Show numeric countdown in reveal button
        }
        await sleep(speed, 'Drawing countdown');
        //Could put small Startup volume increase here too
        if (audio_player.paused) {
            console.log("BEEP! Exiting during a countdown!")
            canceled_during_countdown = true;
            break;
        }
    }
    ctx.clearRect(0, 0, vgm_w, vgm_h);
    ctx.fillText("Ready to Reveal!", vgm_w/2, vgm_h/2+3);
    //Stop playing if we exited during a countdown
    if (canceled_during_countdown) {return}

    //Prep the info box for the reveal
    reveal_msg = `<p><b>Album:</b> ${titleCase(random_album_title)}<br><b>Song:</b> ${titleCase(random_song_title)}</p>`
    let year = random_album['year']
    let platforms = random_album['platforms']
    let developer = random_album['developer']
    let publisher = random_album['publisher']
    if (year !== "") {reveal_msg += `<li><b>Year:</b> ${year}</li>`}
    if (platforms.length !== 0) {reveal_msg +=  `<li><b>Platform(s):</b> ${platforms.join(', ')}</li>`}
    if (developer.length !== 0) {reveal_msg +=  `<li><b>Developer(s):</b> ${developer.join(', ')}</li>`}
    if (publisher.length !== 0) {reveal_msg +=  `<li><b>Publisher(s):</b> ${publisher.join(', ')}</li>`}

    vgm_button.innerText = "...";
    reveal_button.innerText = "Reveal!";
    reveal_button.disabled = false;
}

function reveal() {
    //Disable the revealed button
    const reveal_button = document.getElementById('vgm_reveal_button');
    reveal_button.disabled = true;
    reveal_button.innerText = "Revealed";

    //Display album info
    const info_box = document.getElementById('album_info_box');
    info_box.style.textAlign = 'left';
    info_box.innerHTML = reveal_msg;

    //Swap images
    document.getElementById('question_block_img').style.display = "none";
    document.getElementById('vgm_img').style.display = "block";

    //Write loading-bar message
    let vgm_canvas = document.getElementById('vgm_canvas');
    let ctx = vgm_canvas.getContext('2d')
    ctx.clearRect(0, 0, vgm_canvas.width, vgm_canvas.height);
    ctx.textAlign = 'center';
    ctx.fillStyle = 'skyblue';
    ctx.font = '60px sans-serif bold';
    const confirmation_quotes = ["Did ya guess it?",
                                        "What did you think of this one?",
                                        "Ready for the next song!",
                                        "Sound familiar?",
                                        "Are you ready for another?"]
    ctx.fillText(confirmation_quotes[Math.floor(Math.random() * confirmation_quotes.length)], vgm_canvas.width/2, vgm_canvas.height/2+3)

    //Enable next button
    const next_button = document.getElementById('next_vgm_button');
    next_button.textContent = "Next";
    next_button.disabled = false;
}

function finish_vgm_game() {
    // Stop the music
    const audio_player = document.getElementById('vgm_audio_player');
    audio_player.pause()

    // Re-hide game and show tabs again
    document.getElementById("vgm_game_menu").style.display = "block";
    let temp = document.getElementsByClassName("tab");
    for (i = 0; i < temp.length; i++) {
        temp[i].style.display = "block";
    }
    document.getElementById("the_vgm_game").style.display = "none";
    document.getElementById('vgm_img').src = "";
}