# Worked example: risk assessment of a product change

This is a made-up example to show how I would run a risk assessment on a product change. The company, the feature and every score are invented. It uses the scales and risk tolerance in [METHODOLOGY.md](METHODOLOGY.md).

Built with AI assistance. The scores are my judgments, and I would expect an engineering lead to challenge them.

## The change

A developer platform plans to add **webhook export**. A customer can enter a URL, and the platform sends a message to that URL every time data changes in their project. The messages can include customer records, which may include personal data.

## Scope and assumptions

- In scope: the feature as designed, the platform that sends the messages, and the documentation customers will follow.
- Out of scope: the systems at the receiving end, which belong to the customer.
- Assumption: the customer chooses the URL, and the platform does not check what is behind it unless we add a control.
- Tolerance: a score of 10 or above needs a treatment plan. See METHODOLOGY.md.

## Risks before treatment

| ID | Risk | Likelihood | Impact | Score | Rating |
|---|---|---|---|---|---|
| W-1 | A customer enters an unsecured or wrong URL, so data goes over plain HTTP or to an unintended party | 3 | 4 | 12 | High |
| W-2 | Webhook signing secrets show up in logs or support tickets | 3 | 4 | 12 | High |
| W-3 | A customer enters a URL that points at the platform's own internal systems, and the sending service reaches them | 3 | 5 | 15 | Critical |
| W-4 | Personal data goes to a third party and it is unclear who is responsible for it | 3 | 3 | 9 | Medium |
| W-5 | A burst of events or repeated retries slows delivery for other customers | 3 | 3 | 9 | Medium |
| W-6 | No record that the feature was security reviewed before launch | 3 | 2 | 6 | Medium |

## Treatments and risk after treatment

| ID | Treatment | Owner | When | Likelihood | Impact | Score after | Rating after |
|---|---|---|---|---|---|---|---|
| W-1 | Mitigate: accept HTTPS URLs only, sign every message, document how to verify the signature | Engineering lead | Before launch | 2 | 4 | 8 | Medium |
| W-2 | Mitigate: hide secrets in logs, check existing logs for the pattern, add a reminder to the support process | Security | Before launch | 1 | 4 | 4 | Low |
| W-3 | Mitigate: block private and internal address ranges, check the address again at send time, send from an isolated network, test it in a penetration test | Security and Engineering lead | Before launch | 1 | 5 | 5 | Medium |
| W-4 | Mitigate: state in the docs and terms that the customer is responsible for the receiving end, legal review of the wording | Legal | Before launch | 2 | 2 | 4 | Low |
| W-5 | Mitigate: per-project rate limits, retry delays that grow, separate queue for webhook traffic | Engineering lead | Before launch | 2 | 2 | 4 | Low |
| W-6 | Mitigate: open a security review ticket and link it in the change record | Compliance | Before launch | 1 | 2 | 2 | Low |

## Recommendation for leadership

1. **Do not launch until W-3 is treated.** It is the only Critical risk, and an attack through it would reach internal systems. It should not be accepted. If the launch date cannot move, leadership would need to sign the acceptance by name, and I would recommend against it.
2. **W-1 and W-2 are above tolerance and need their treatments in place before launch.** Both have clear, small fixes.
3. **W-4, W-5 and W-6 are below tolerance.** The owner can accept them, but the fixes are cheap, so I would do them anyway.
4. After launch, re-test W-3 and W-5 once the feature has real traffic, and add any risk still above tolerance to the risk register.

## Questions I would ask engineering before finalizing

- Which fields can a message contain, and can a customer limit them?
- Does the sending service run in the same network as anything internal?
- How are retries handled, and is there a limit per project?
- Are request bodies or headers written to logs anywhere?

## What this example does not cover

It does not score the receiving side, and it does not test whether the treatments work. A treatment on this list is only a plan until someone tests it. In practice I would add a control test for each Critical or High risk, the way the tests in my grc-control-tests repo work.
