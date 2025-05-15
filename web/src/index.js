(async () => {
	console.debug('initializing...');

	// Get episode title, number, YouTube URL from seed
	function getEpisodeDataFromSeed(seedID) {
		return episodeData[seedID];
	}

	// bracket item element constructor
	function createBracketItem(seedID) {
		const bi = document.createElement("div");
		bi.classList.add("bracket-item");

		const bis = document.createElement("span");
		bis.classList.add("bracket-item-name");

		bis.setAttribute("data-seed-id", seedID);

		// seedID will be -1 for undeclared winner slots etc.
		if (seedID > 0) {
			const ed = getEpisodeDataFromSeed(seedID);

			if (ed["link"] === "") {
				bis.innerText = `${ed['title']}`
			} else {
				const a = document.createElement("a");
				a.href = ed["link"];
				a.target = "_blank";
				a.rel = "noopener";
				a.innerText = ed["title"];

				bis.appendChild(a);
			}
		} else {
			bis.innerText = "tbd";
		}

		bi.appendChild(bis);

		return bi;
	}

	function buildBracketStructure(roundData, roundID, level) {
		console.debug("[buildBracketStructure]", "roundID is", roundID, "roundData is", roundData);

		// I'm sure I could template all this crap but idc (^:
		const group = document.createElement("div");
		group.classList.add("group");
		group.classList.add(`level-${level}`);

		const entries = document.createElement("div");
		entries.classList.add("entries");

		const winnerWrapper = document.createElement("div");
		winnerWrapper.classList.add("winner-wrapper");

		const winner = document.createElement("div");
		winner.classList.add("winner");

		const winnerWhitespace = document.createElement("div");
		winnerWhitespace.classList.add("winner-whitespace");

		winner.appendChild(createBracketItem(roundData["winner"]));
		winnerWrapper.appendChild(winner);
		winnerWrapper.appendChild(winnerWhitespace);

		// deepest level is an array of seedIDs
		if (Array.isArray(roundData["entries"])) {
			console.debug("[buildBracketStructure]", "building entries from seedID array", roundData["entries"]);

			roundData["entries"].forEach((seedID) => {
				entries.appendChild(createBracketItem(seedID));
			});

			entries.classList.add(`level-${level + 1}`);
		} else {
			console.debug("[buildBracketStructure]", "recursing down the tree!");

			++level;

			// recurse down this mf!
			for (let [k, v] of Object.entries(roundData["entries"])) {
				const bs = buildBracketStructure(v, k, level);

				bs.setAttribute("id", `round-${k}`);

				entries.appendChild(bs);
			}
		}

		// TODO: Add background color to highlight winning entries?

		group.appendChild(entries);
		group.appendChild(winnerWrapper);

		return group;
	}

	function populateOverallWinner(seedID) {
		const elem = document.querySelector("#overall-winner > h2");
		const epData = getEpisodeDataFromSeed(seedID);

		elem.innerHTML = `<a href="${epData['link']}" target="_blank" rel="noopener">${epData['title']}</a>`;
	}

	function hideBracketLevels(level) {
		const maxLevel = 6;

		// pass -1 to unhide everything
		if (level < 0) {
			console.debug("[hideBracketLevels]", "Unhiding all bracket levels...");

			for (let i = 0; i <= maxLevel; ++i) {
				const toUnhide = document.querySelectorAll(`.level-${i}`);

				console.debug("[hideBracketLevels]", "Unhiding", toUnhide.length, "items from level", i);

				toUnhide.forEach((el) => {
					el.classList.remove("hidden");
				});
			}

			console.debug("[hideBracketLevels]", "Done unhiding all bracket levels!");

			document.documentElement.style.setProperty("--bracket-columns", "15");

			return;
		}

		const newColumnCount = level * 2 + 1;

		console.debug("[hideBracketLevels]", "Hiding bracket level", level, "...");

		// HACK: this is so freaking stupid but I'm #vibecoding
		hideBracketLevels(-1);

		// .level-6 is the outermost (earliest) rounds
		// increasing levels contain previous levels so we don't need to hid everything
		const toHide = document.querySelectorAll(`.level-${level}`);

		console.debug("[hideBracketLevels]", "Found", toHide.length, "items to hide...");

		toHide.forEach((el) => {
			el.classList.add("hidden");
		});

		console.debug("[hideBracketLevels]", "Setting --bracket-columns to", newColumnCount, ".");

		document.documentElement.style.setProperty("--bracket-columns", newColumnCount);

		console.debug("[hideBracketLevels]", "Done hiding items from level", level, "!");
	}

	// --------------------------------------------------------------------------
	// Everything below this comment is the "main" function :^)
	// --------------------------------------------------------------------------

	console.info("start it!");

	const hideLevelSelect = document.querySelector("#toggle-levels");

	// Reset this to "none" on page reload
	hideLevelSelect.value = -1;

	hideLevelSelect.addEventListener("input", (e) => {
		const v = parseInt(e.target.value);
		console.debug("[main]", "handling input event for toggle-levels select with value", v);
		hideBracketLevels(v);
	})

	// Pass these options to fetch() calls so they work with <link rel="preload" as="fetch"> from the HTML
	// https://stackoverflow.com/a/63814972/3722806
	const fetchOpts = {
		method: 'GET',
		credentials: 'include',
		mode: 'no-cors',
	}

	const bracketStructure = await (await window.fetch("data/structure.min.json", fetchOpts)).json();
	const episodeData = await (await window.fetch("data/episodes.min.json", fetchOpts)).json();

	console.debug(episodeData);
	console.debug(bracketStructure);

	const leftBracketData = bracketStructure["141"]["entries"]["139"];
	const rightBracketData = bracketStructure["141"]["entries"]["140"];

	const lbc = document.querySelector("#left");
	const rbc = document.querySelector("#right");

	console.log("[main]", "Populating left side of the bracket...");
	lbc.appendChild(buildBracketStructure(leftBracketData, "139", 0));

	console.log("[main]", "Populating right side of the bracket...");
	rbc.appendChild(buildBracketStructure(rightBracketData, "140", 0));

	// HACK: This shouldn't be hardcoded lol
	const overallWinnerSID = bracketStructure["141"]["winner"];
	if (overallWinnerSID > 0) {
		populateOverallWinner(overallWinnerSID);
	}

	// if (urlParams.has("hide")) {
	// 	const hideLevel = parseInt(urlParams.get("hide"));

	// 	switch (hideLevel) {
	// 		case 1:
	// 			const elems = document.querySelectorAll(".level-6");
	// 			elems.forEach((el) => {
	// 				el.classList.add("hidden");
	// 			})
	// 			break;

	// 		default:
	// 			break;
	// 	}
	// }

	// HACK: yeah this looks like cheeks on phones right now. let's make the alert
	// look like cheeks too
	// (use a small timeout so the page renders in first)
	window.setTimeout(() => {
		if (window.innerWidth < window.innerHeight || window.innerWidth < 1200) {
			alert("hey what's up :D\n\nthis site kinda looks like butt on moble/small screens right now. sorry about that.\n\nanyway go ahead and hit \"OK\" just know you're gonna have to scroll around a bunch.\n\n\t—audrey");
		}
	}, 100);

	console.info('finished doing literally everything :steamhappy: ');
})();
