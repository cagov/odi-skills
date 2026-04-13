# How to use Claude skills

A skill is a set of rules that tells Claude how to do a specific kind of work. When you load a skill, Claude follows those rules on its own. You do not need to explain your context, standards, or preferences each time.

ODI builds skills for work we do often. Each skill covers a specific task, like rewriting text in plain language. Skills save time and keep our work steady.

---

## How skills work

Skills are interactive. Claude will ask you questions, guide you through steps, and check in along the way. This is normal. The more you engage, the better the result.

Each skill has trigger phrases. These are short commands that tell Claude what you want. They are listed in the skill's guide. You can also paste your content and describe what you need. Claude will pick the right skill.

---

## Install a skill

Skills come as `.skill` files. In this repository they live under `releases/` and are part of the git tree — clone the repo or open that folder on GitHub and download the file you need.

1. Download the .skill file. Save it to your desktop.
2. Open Claude. Expand the sidebar on the left.
3. Select the Customize tab.
4. Find the Skills section and open it.
5. Select + to upload a skill.

You can install more than one skill at a time. Claude will use the right one based on your request.

---

## Update a skill

ODI updates skills over time. When a new version is ready:

1. Download the updated .skill file.
2. Follow the install steps above.
3. Choose "Upload and replace" when asked.

We suggest replacing old versions instead of keeping both. You can always switch back if needed.

---

## Available skills

|Skill|What it does|
| --- | --- |
|Example: ODI plain language | Rewrites text to meet the ODI Plain Language Equity Standard. Works for Slack, emails, memos, briefings, blog posts, and case studies.|
|[TODO: add skills as they are published] | |

---

## Tips

* **Use the best model.** Skills for complex tasks may work better with Opus than Sonnet or Haiku.
* **Start a new conversation for each task.** Skills work better in a fresh chat than in a long thread with mixed topics.
* **Follow the prompts.** Skills ask questions on purpose. Answer them. Skipping ahead usually gives a weaker result.
* **Work in sections for long content.** If your document is more than a page or two, let Claude break it into parts. You will get a better edit.

---

## Support

If you find an issue with a skill, please submit a GitHub issue. Include which skill and suggestions for improvements.