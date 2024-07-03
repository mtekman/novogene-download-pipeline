const puppeteer = require('puppeteer')
const fs = require('fs')
const path = require('path')
const { promisify } = require('util')

const readFileAsync = promisify(fs.readFile)
const writeFileAsync = promisify(fs.writeFile);

(async () => {
    const browser = await puppeteer.launch({
        headless:"new",
        product: "chrome",
        executablePath:"/usr/bin/chromium"
    })
    const page = await browser.newPage()
    await page.setViewport({ width: 1200, height: 800 })

    await page.goto('https://ocsseurope.novogene.com/oauth/login')
    await page.type('#username', process.env.USERLOG)
    await page.type('#password', process.env.PWDLOG)

    const submit_button = await page.waitForSelector('button.btn-login.btn-raised');
    await submit_button.click()

    // Onto the main page
    await page.waitForNavigation()

    // Then move onto a download page
    //e.g. X204SC23032919-Z01-F004'
    await page.goto('https://csseurope.novogene.com/pub/projects/home?tab=dataRelease&BatchNo=' + process.env.BATCHNO)

    // Wait for page to load before evaluating it
    await page.waitForSelector("tr > td > span");
    await page.waitForTimeout(1000);

    // Set button identifier in the page. This is a hack, but it works.
    await page.evaluate((batchno) => {
        const find_spans = document.querySelectorAll("tr > td > span");
        const find_spans_arrays = Array.from(find_spans)
        const get_row = find_spans_arrays.find(x => x.textContent === batchno);
        butt = get_row.parentNode.parentNode.querySelector("img.normal[alt='download']").parentNode.parentNode;
        butt.id= "GETTHIS"
    }, process.env.BATCHNO);

    
    await page.waitForTimeout(1000);
    const butt = await page.waitForSelector("#GETTHIS")
    butt.click()
    await page.waitForTimeout(3000)

    // New download page
    const page2 = await browser.newPage()
    const viewSource = await page2.goto("https://data-deliver.novogene.com/api/file/GetBatchFiles?BatchNo=" +
        process.env.BATCHNO, { waitUntil: 'networkidle2' })
   
    const buffer = await viewSource.buffer()
    console.log((await viewSource.json()))
    await writeFileAsync(path.join(__dirname, 'batch.json'), buffer)
    console.log('The file was saved!')

    browser.close()
})()
