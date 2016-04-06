# Contributing to 'jailify'
These are the guidelines for contributing to 'jailify'. Exceptions can always be
made, but these guidelines exist for a reason and ought to keep workflow, code,
and documentation in order. Please review them thoroughly before attempting to
contribute. If it's obvious that you haven't read any of these guidelines it's
unlikely your contributions will be accepted.

## Repository Management
Repository management is a tricky thing to get right. The preferred model for
`jailify` is to have a [central repository][repo] that all contributors fork. No
changes should reach the `master` branch except by way of a [merge request]. We
suggest that contributors keep the master branch of their fork and local
repositories up-to-date with the central repository. Ideally modifications
should be made on branches and merge requests submitted from said branches.

## Submitting Issues
Issues can be for **anything**, not just bugs. Find some incorrect
documentation? Submit an issue! Is there a function that's logically sound, but
butchers the code style conventions? Submit an issue! Do you want the software
to support a new feature? Submit an issue! Better yet, fix the problem yourself
and submit a [merge request].

#### Bug Reports
A bug is a _demonstrable problem_ caused by code in the repository.

When submitting a bug report:
1. **Search for the issue** &mdash; check if the issue has already been
   reported.

2. **Check if the issue has been fixed** &mdash; try to reproduce it using the
   latest `master` or development branch in the repository.

3. **Isolate the problem** &mdash; try to narrow down the cause of the bug.
   Include an example in your report.

Example:

> Short and descriptive example bug report title
>
> A summary of the issue and the browser/OS environment in which it occurs. If
> suitable, include the steps required to reproduce the bug.
>
> 1. This is the first step
> 2. This is the second step
> 3. Further steps, etc.
>
> Any other information you want to share that is relevant to the issue being
> reported. This might include the lines of code that you have identified as
> causing the bug, and potential solutions (and your opinions on their
> merits).

#### Feature Requests
Feature requests are welcome, but please consider whether your idea fits within
the project scope. Provide as much detail as possible. For example, a feature
request like
> Use YAML for configuration because it's better than JSON.

is unlikely to be given any thought. An alternative like
> Use YAML for configuration in place of JSON since YAML supports references
> and multiline strings which could be useful for deployment in multiple
> environments and better formatting of SQL statements.

is **much** more likely to be considered.

#### Merge Requests
Merge requests are _wonderful_ help. They should remain focused, in scope, and
avoid containing unrelated commits (see [topic branch] model). Make sure your
merge request contains a clear title and description.

It's a good idea to **ask** before undertaking any work on a significant merge
request, otherwise you risk doing a lot of work for something the rest of the
developers might not want to merge.

Be sure to follow the guidelines on [writing code](#writing-code) if you want
your work considered for inclusion.

### Handling Merge Requests
- Merging your own merge request defeats the purpose. You might as well
  `git push --force` to `master`. Except in rare circumstances no one should
  accept their own merge request.

- When possible there should be more than one reviewer with eyes on the code
  before a merge request is actually accepted.

- For all but the most trivial merges involving code a reviewer should actually
  pull down the modified code and verify that it works before accepting.

### Issue and Merge Request Conventions
From the [GitLab Flow] documentation:
> It's common to voice approval or disapproval by using :+1: or :-1:. In GitLab
> you can use emojis to give a virtual high five on issues and merge requests.

Show the submitter you either approve or disapprove of their suggestions. It's
also common to see :heart: and :ship: (for "ship it!") as emojis. Obviously
these emojis should go hand in hand with concrete feedback.



## Writing Code
So you want to add (or perhaps remove) some code. Great! Please adhere to these
guidelines to ensure coherence throughout the application.

### Coding Style
- Follow most [PEP8] guidelines. There can be some flexibility with regard to
  line length and naming, but in general PEP8 provides a solid set of rules.

- Strive to follow Tim Peters' _The Zen of Python_ (`import this`) where
  possible.

### Version Control
- [Fork][forking] the [central repository][repo] and work from a clone of your
  own fork.

- Follow the [topic branch][topic branch] model and submit merge requests from
  branches named according to their purpose.

- Review the [GitLab Flow] documentation and, in general, try to stick to the
  principles outlined there.

## Shout-outs
- Much thanks to [Nicolas Gallagher] for his generic [issue guidelines].

[repo]: https://gitlab.***REMOVED***/cs-support/adctl
[merge request]: https://gitlab.***REMOVED***/help/workflow/forking_workflow.md#merging-upstream
[GitLab Flow]: http://doc.gitlab.com/ee/workflow/gitlab_flow.html
[PEP8]: https://www.python.org/dev/peps/pep-0008/
[forking]: https://gitlab.***REMOVED***/help/workflow/forking_workflow.md
[topic branch]: https://git-scm.com/book/en/v2/Git-Branching-Branching-Workflows#Topic-Branches
[Nicolas Gallagher]: http://nicolasgallagher.com/
[issue guidelines]: https://github.com/necolas/issue-guidelines
