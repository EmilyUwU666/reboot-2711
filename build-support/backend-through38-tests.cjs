'use strict';
// Exercise the real pinned backend with synthetic season-tagged requests.
// This does not run Fortnite or validate native hooks/gameplay.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const {spawn} = require('node:child_process');
const {once} = require('node:events');
const root = path.resolve(process.argv[2] || 'backend-source');
const scratch = fs.mkdtempSync(path.join(os.tmpdir(), 'reboot-seasons-test-'));
let child;
let output = '';
let checks = 0;
const expect = (ok, label) => { assert.ok(ok, label); ++checks; };
const wait = ms => new Promise(resolve => setTimeout(resolve, ms));
async function request(release, url, method = 'GET', body, extraHeaders = {}) {
    const response = await fetch('http://127.0.0.1:3551' + url, {
        method, body: body === undefined ? undefined : JSON.stringify(body),
        headers: {...extraHeaders, 'content-type': 'application/json', 'user-agent': `Fortnite/++Fortnite+Release-${release}-CL-${release === '38.00' ? '47722112' : '1'} Windows/10`},
        signal: AbortSignal.timeout(10000)
    });
    expect(response.status === 200, `${release} ${method} ${url}: HTTP ${response.status}`);
    return response;
}
async function main() {
    child = spawn(process.execPath, ['start-backend.cjs'], {cwd: root, env: {...process.env, LOCALAPPDATA: scratch}, stdio: ['ignore', 'pipe', 'pipe']});
    child.stdout.on('data', data => { output += data; });
    child.stderr.on('data', data => { output += data; });
    for (let i = 0; i < 150 && !output.includes('XMPP and Matchmaker started listening on port 80'); ++i) {
        if (child.exitCode !== null) throw new Error('Backend failed to start');
        await wait(100);
    }
    expect(output.includes('XMPP and Matchmaker started listening on port 80'), 'backend is ready');
    const releases = ['19.40', '20.40', '21.51', '22.40', '23.50', '24.40', '25.30', '26.30', '27.11', '28.30', '29.40', '30.40', '31.00', '32.00', '33.00', '34.00', '35.00', '36.00', '37.00', '38.00', '19.40'];
    for (const release of releases) {
        const season = Number(release.split('.')[0]);
        const branch = '++Fortnite+Release-' + release;
        const token = await (await request(release, '/fortnite/api/discovery/accessToken/' + encodeURIComponent(branch))).json();
        expect(token.branchName === branch && token.appId === 'Fortnite' && token.token?.length > 0, `${release} discovery-token schema`);
        for (const url of ['/discovery/surface/page', '/api/v2/discovery/surface/page']) {
            const surface = await (await request(release, url, 'POST', {})).json();
            expect(Array.isArray(surface.Panels) && surface.Panels.some(panel => (panel.Pages || []).some(page => (page.results || []).some(item => item.linkData?.mnemonic === 'playlist_defaultsolo'))), `${release} Solo discovery data`);
        }
        const response = await (await request(release, '/fortnite/api/game/v2/profile/season-test/client/QueryProfile?profileId=athena&rvn=-1', 'POST', {})).json();
        const profile = response.profileChanges?.find(change => change.changeType === 'fullProfileUpdate')?.profile;
        expect(profile?.stats?.attributes?.season_num === season, `${release} profile carries matching season, including switching back to 19`);
        // Synthetic network ID; this is not the executable's net version.
        const networkId = String(100000 + season);
        const ticket = await request(release, '/fortnite/api/game/v2/matchmakingservice/ticket/player/season-test?bucketId=' + networkId + ':0:EU:playlist_defaultsolo');
        const cookie = ticket.headers.get('set-cookie')?.split(';')[0];
        expect(cookie === 'currentbuildUniqueId=' + networkId, `${release} ticket preserves network ID`);
        const ticketBody = await ticket.json();
        expect(ticketBody.serviceUrl === 'ws://127.0.0.1' && ticketBody.ticketType === 'mms-player', `${release} local matchmaker ticket`);
        const match = await (await request(release, '/fortnite/api/matchmaking/session/season-test', 'GET', undefined, {cookie})).json();
        expect(match.buildUniqueId === networkId, `${release} session preserves network ID from cookie`);
        expect(match.serverAddress === '127.0.0.1' && match.serverPort === 7777, `${release} local game-server destination`);
        const timeline = await (await request(release, '/fortnite/api/calendar/v1/timeline')).json();
        const states = timeline.channels?.['client-events']?.states || [];
        expect(states.some(state => state.state?.seasonNumber === season), `${release} timeline season`);
        expect(states.some(state => state.activeEvents?.some(event => event.eventType === `EventFlag.Season${season}`)), `${release} timeline event`);
        const config = await (await request(release, '/fortnite/api/cloudstorage/system/DefaultEngine.ini')).text();
        expect(config.includes('ServerPort=80'), `${release} XMPP configuration`);
        console.log(`Season ${season} HTTP/profile checks passed (${release}, ${release === '38.00' ? 'observed CL 47722112' : 'synthetic CL 1'})`);
    }
    console.log(`${checks} cross-release backend checks passed across all twenty release majors and a return to Season 19`);
}
main().catch(error => { console.error(error.stack || error); console.error(output.slice(-8000)); process.exitCode = 1; })
    .finally(async () => {
        if (child && child.exitCode === null) { const ended = once(child, 'exit'); child.kill(); await ended; }
        fs.rmSync(scratch, {recursive: true, force: true});
    });
