/* eslint-env node */
/* eslint-disable no-console */

// dependencies
const path = require('path');
const fs = require('fs');
const fsExtra = require('fs-extra');
const utils = require('./_utils');

const projectName = utils.getProjectName();
const sourceDir = utils.getSourceDir(projectName);
const outDir = utils.getOutDir(projectName);
utils.createProjectDistDir(projectName);

// all static file/dir names to check for
let possibleStaticFiles = [ `index.html`, `img`, `assets`, `fonts` ];

// copy statics if they exist
for(let file of possibleStaticFiles) {
  const fullPath = path.resolve(sourceDir, file);

  if(fs.existsSync(fullPath)) {
    const outPath = path.resolve(outDir, file);
    console.log(`Copying ${fullPath} to ${outPath}`)
    fsExtra.copySync(fullPath, outPath);
  }
}
