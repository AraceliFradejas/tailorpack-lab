import {cp, mkdir, rm} from 'node:fs/promises';
const root = new URL('../', import.meta.url);
await rm(new URL('dist/', root), {recursive:true, force:true});
await mkdir(new URL('dist/', root), {recursive:true});
await cp(new URL('public/', root), new URL('dist/', root), {recursive:true});
console.log('Static app built in dist/ — no runtime server or dependencies.');
