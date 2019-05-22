# EBDraw
This application lets you enter the Travis Scott raffle (or any other raffle) even when the page is taken down.

The original draw application was made by a third party Ziad Javed who apparently built this app for Extra Butter. It appears that Renarts uses the same application. I'm sure with some tweaks this would work for them too.

You could take advantage of the threading in this app to submit one entry or thousands of entries.

Their backend is tied to Shopify's Customer API so whatever account you enter needs to have an existing account on their site. You can make one here: https://shop.extrabutterny.com/account/register

## Installation / Config
Clone down and run `main.py` after configuring `config.json` with your details. Requires Python 3.x.

Make sure you have an address associated with your account. Check on that here: https://shop.extrabutterny.com/account/addresses

Don't forget to install requirements `pip install -r requirements.txt`.

You'll need a Shopify account on their site that has a saved address associated with it, and you'll need to know the Shopify product ID for the raffle you'd like to enter.

The PID for the Travis Scott AJ1 is `2344424308784`. I wouldn't bother too much, it looks like they only have 1 pair per size.

## How it works
The script logs into your customer account with EB and gathers some details. Then it gathers the variant ID's associated with the raffle and makes a new entry with aforementioned account details. Then it tokenizes the CC info via stripe and ties that together with the new entry. Pretty simple.

## Notes
EB really needs to do some work with their draw application. It is not very secure and seems like it would be succeptible to some well placed XSS attacks. It appears they don't sanitize the inputs to their Heroku app very well (hint: try POSTing some form data with a ;). From what I've discovered, it looks like it's running Symfony PHP to route requests.

Their app went down almost all day and was completely unresponsive. Guessing that's because it was slammed with requests. They should probably enable some scaling to fix that.

Furthermore, their current application (as of 5/6/19) will reveal intimate address details if you submit just a simple email address and valid ReCaptcha challenge token alongside it. Seems like a big no-no to me, but hey what do I know.

Anyway, have fun. If you win some shoes because of this (you have a better chance of getting in a car accident) then throw me a shoutout on twitter: @edzart.
