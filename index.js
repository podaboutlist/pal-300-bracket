"use strict";

let g_episodeData;
let g_bracketStructure;

(async () => {
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
			bis.innerHTML = `<a href="${ed['link']}" target="_blank">${ed['title']}</a>`;
		} else {
			bis.innerText = "tbd";
		}

		bi.appendChild(bis);

		return bi;
	}

	function buildBracketStructure(roundData) {
		console.debug("roundData is ", roundData);

		// I'm sure I could template all this crap but idc (^:
		const group = document.createElement("div");
		group.classList.add("group");

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
			console.debug("buildBracketStructure: building entries from seedID array", roundData["entries"]);

			roundData["entries"].forEach((seedID) => {
				entries.appendChild(createBracketItem(seedID));
			});
		} else {
			console.debug("buildBracketStructure: recursing down the tree!");

			// recurse down this mf!
			for (let [k, v] of Object.entries(roundData["entries"])) {
				const bs = buildBracketStructure(v);

				bs.setAttribute("id", `round-${k}`);

				entries.appendChild(bs);
			}
		}

		group.appendChild(entries);
		group.appendChild(winnerWrapper);

		return group;
	}

	const episodeData = await (await window.fetch("data/episodes.json")).json();
	const bracketStructure = await (await window.fetch("data/structure.json")).json();

	// for testing
	g_episodeData = episodeData;
	g_bracketStructure = bracketStructure;

	console.log(episodeData);
	console.log(bracketStructure);

	const leftBracketData = bracketStructure["141"]["entries"]["139"];
	const rightBracketData = bracketStructure["141"]["entries"]["140"];

	const lbc = document.querySelector("#left");
	const rbc = document.querySelector("#right");

	console.log("Populating left side of the bracket...");
	lbc.appendChild(buildBracketStructure(leftBracketData));

	console.log("Populating right side of the bracket...");
	rbc.appendChild(buildBracketStructure(rightBracketData));
})();
