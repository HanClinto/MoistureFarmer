# MoistureFarmer
An experimental *sand*box in agentic AI. A thrilling simulator where you play the exciting life of a moisture farmer on a distant desert planet. If you can automate enough of your daily tasks with your droid companions, maybe you'll have enough time to visit Tosche Station this weekend!

## Getting Started

```
cd code
pip install -r requirements.txt
bash start_webgui.sh
```

Then in a browser, navigate to 127.0.0.1:8000

Still highly experimental. Been working on the GUI lately, so agentic loops are currently disconnected -- to be reconnected soon!

## Design Philosophy

### Strong Separation between Simulation vs. GUI

This system is designed to run "headless" (as an agentic AI benchmark), and also run with a GUI attached to it.

We've experimented with a few different methods, but currently the back-end runs in Python and publishes game-world updates once-per tick to all subscribers vs. SSE.

This may be overkill for a single-player game, but this was chosen because:

* HTML gives us a rendering engine with a bunch of nice controls that let us quickly build GUIs and (generally) lay things out like a hierarchical JSON tree view with minimal fuss.

* The [98.css](https://jdan.github.io/98.css/) library is so beautifully done, and lets us emulate the look-and-feel of [classic Windows 98 games](https://collectionchamber.blogspot.com/p/star-wars-yoda-stories.html) with relative ease.

### Simulation first, game second

While this is (eventually) intended to be a playable game (in the vein of Stardew Valley), the primary goal is to be a rich simulation sandbox for experimenting with multi-agent AI systems using LLMs with tool-calling.

Would it be possible to attach various modular implements to Roombas with minimal human instruction and let them roam around your house, accomplishing your daily tasks? That's the sort of thing that this environment is meaning to find out!

### Component-based, modular structure

A chassis holds one or more components. Each piece of equipment is a chassis, and has slots that can hold various kinds of equipment.

For instance:

* R2 Astromech:
  * 1 Class II processor slot
  * 1 Motivator slot
  * 4 Manipulator slots (general-purpose tools, like saws or torches or grabbers)
  * 1 Power Pack slot
  * 1 Computer Probe slot

* EG-6 "Gonk" Droid:
  * 1 Class V processor slot
  * 1 Motivator slot
  * 1 Power Pack slot
  * 1 Power Converter slot

A chassis can hold one or more pieces of equipment in its slots. I added some views in the assets folder for nice schematic-looking profile images for each of the robot types -- don't need to use these now, but I was kinda' imagining an RPG-esque interface for being able to equip various components onto your droids.

And can fit items into the various slots -- and then arrange the components in the various slots like an old RPG.

There are lots of item graphics in the ripped section -- sensor arrays, power converters, motivators, processors, etc.

Each piece of equipment adds functionality and/or tool-call capabilities. For instance:

* A Motivator on a droid adds the move_to_location and move_to_object commands.

* A Power Converter allows it to Charge something else.

* A Computer Probe allows it to connect to other machines to program them or pull information.

* A Condenser Unit in a Vaporator uses power to cool down and condense water out of the air, filling any attached Water Tank for later retrieval.


Other manipulators would let the droids clean, remove, replace, and repair broken or worn parts on other machines, or even assemble new droids out of scrap parts (self-assembling droid factory, anyone?)

We could start with simple stats for each object, like Durability and Health, but could also consider things like Sand (it's coarse and rough and it gets everywhere), and don't forget C-3PO's oil bath -- lubricating frozen joints is important for droid happiness and functionality. :)

Each equipment can have stats, functions, and an on_tick() routine that gets called and updates itself (and appropriate pieces of the world around it).

### Context-engineering in the world of agentic AI

If the droid's context gets corrupted -- either through hallucinations, or invalid tool calls, or wonky ideas where it gets stuck in a weird loop, or just gets to be too darn large for the token limit on your LLM -- once we reach a certain number of errors (could be 1, could be 10 -- whatever we set the threshold to be), then the droid could "blue screen" and reboot itself, thereby clearing its context, and starting fresh from a regular day's fresh prompt.

I was already imagining that all droids and equipment would be shut off at the end of every day and start with a fresh new context every morning -- but if a droid gets too many errors, there's no reason why it couldn't get rebooted (either by the player, or automatically due to errors) and clear its own context and try again.

It still might result in loops of some sort, but it's a fun idea to think about.

It's easy to add a text box to allow users to enter in the prompts to control the droids and make that the "game", but it's less easy to give the player hooks for culling the context. How do we gamify context-engineering? This needs to be explored. If you have any ideas, I'd love to hear them!

### Scenario-based Challenges

I am structuring the tests as simple scenarios to challenge the game environment, but eventually want to use this as a gauntlet to evaluate the performance of various LLMs and prompting / context-engineering mechanisms.

Given these starting conditions, how well does X model perform on this suite of tests?

Right now I'm imagining setting things up with days / scenarios so that we can test the viability of the system.

* Day 1)
  * 1 vaporator, 10% charge
  * Gonk droid
    * Travel to (single) vaporator
    * Charge it
    * Return to base
    * Switch off


* Day 2)
  * 2 vaporators, 10% and 5% charge
  * Gonk droid
    * Travel to first vaporator (nearest or lowest?)
    * Charge it
    * Travel to next
    * Charge it
    * Travel home
    * Switch off

* Day 3)
  * 1 vaporator (10%), 1 generator
  * Gonk droid (10% charge)
    * Travel to generator
    * Charge self
    * Travel to vaporator
    * Charge it
    * Travel home
    * Switch off

Later days would add additional droids and tasks (collect water, clean equipment, tune equipment, repair equipment) and even hostiles (equipment degradation, sandstorm, tusken raiders, maybe a krayt dragon) and these could serve as unit tests for our system to test prompts in controlled and repeatable environments.

I'm curious to know how small of a prompt on each droid we could use to solve each challenge.

And once we graduate to turning this simulator into a game, these scenarios could be used as a tutorial progression of sorts before unleashing the player into the context of the full sandbox.

I want to use this as a benchmark for evaluating the zero-shot capability of various tool-calling LLMs, and also use this as a benchmark that others can use to explore multi-agent systems.

In the context of a game, these scenarios will form a tutorial-like progression, but in the context of a benchmark, these scenarios will form the test suite to evaluate model or prompting performance.

## Running Tests in Docker

Build the test image:

```bash
docker build -f Dockerfile.test -t moisture-tests .
```

Run the test suite:

```bash
docker run --rm moisture-tests
```

You can mount the workspace to re-run quickly without rebuilding (slower initial startup due to installing deps inside container each run):

```bash
docker run --rm -v $(pwd)/code:/app/code moisture-tests
```
