"use strict";

(() => {
	const populateBracket = (bracketData) => {
		bracketData.forEach((episode) => {
			const seedID = episode["Seed"];

			const slots = document.querySelectorAll(`span[data-seed-id='${seedID}']`);

			if (slots.length < 1) {
				return;
			}

			// I forget how O(n) notation works but nested forEach loops cannot possibly be good :steamhappy:
			slots.forEach((slot) => {
				slot.innerHTML = `<a href="${episode['Link']}" target="_blank">${episode['Episode Title']}</a>`;
			});
		});
	}

	Papa.parse("data/tourney-seeds.csv", {
		header: true,
		download: true,
		complete: (res) => {
			populateBracket(res.data);
		}
	});
})();
