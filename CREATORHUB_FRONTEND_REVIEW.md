# Nestar frontend review and CreatorHub migration plan

Reviewed 27 September 2026.

Frontend: `/Users/kakhkhorov/Desktop/nestar-next`.
Backend: `/Users/kakhkhorov/Desktop/creatorhub-backend-starter`.

## Opinion

This is a useful unfinished starter. Next.js, React, Apollo, MUI, translation setup, shared layouts, cards, filtering patterns, and dashboard structure give us material to reuse. The TypeScript compiler and production build both pass. We should preserve useful structure and your familiarity with it.

The current implementation still describes a real-estate product. CreatorHub needs separate account identities, creator profiles, portfolio projects, service offerings, and private inquiries. A property cannot represent both a portfolio project and a service. Replacing names without replacing the data and workflows would leave the application inconsistent.

My recommendation is an incremental conversion in a separate CreatorHub frontend folder, with Nestar preserved as the reference. Keep Next.js, Apollo, and MUI initially. Retaining the Pages Router is reasonable for the first working integration. A router migration is a separate decision, not a prerequisite for this product.

## Verification and limits

- Frontend `tsc --noEmit --incremental false` passed.
- A production build of a temporary source copy passed, including 73 generated pages across locales. The original frontend source was not edited.
- Validated all 36 GraphQL documents in the four `apollo/user` and `apollo/admin` files against `docs/schema.graphql`. All 36 are invalid against CreatorHub. This count excludes inline multipart upload documents, which also use operations absent from CreatorHub.
- Direct ESLint execution failed because the frontend has no ESLint configuration. Do not treat the build's linting heading as evidence that lint passed. The package also pairs Next 14.2.0 with `eslint-config-next` 12.1.0.
- Inspected the homepage and login route in the in-app browser. At a 390px-wide viewport, the login document measured 1,300px wide. This was viewport emulation with the browser's desktop user agent, not a physical phone test. Phone user agents select placeholder branches according to the source.
- Build output reported homepage first-load JavaScript of 518 kB, versus 265 kB for the login route. These are Next build estimates, not measured download times or Core Web Vitals.
- Build output included translation initialization and outdated Browserslist warnings. They did not block compilation.
- Backend review included source, generated schema, API examples, integration documentation, and work logs. The backend's existing review records 48 passing tests. I did not rerun its tests or verify live social, email, storage, or AI integrations during this frontend review.
- Impeccable's context/detector engine is unavailable locally. The findings below come from source inspection, schema validation, compilation, and the browser check. No automated design-detector or full WCAG certification is claimed.
- The temporary preview server was stopped after inspection. No accounts, inquiries, or other backend records were created.

## Findings in priority order

### P1: API contract mismatch blocks CreatorHub integration

`apollo/user/query.ts`, `apollo/user/mutation.ts`, and their admin equivalents use operations and fields such as `getProperties`, `getAgents`, `MemberInput`, `memberNick`, and `metaCounter`. CreatorHub exposes `getProjects`, `getCreators`, `RegisterInput`, `displayName`, and bounded array lists.

Even the shared `login` name has a different input and output contract. CreatorHub returns `accessToken`, `refreshToken`, `expiresIn`, and a nested `user`. Existing account code expects member fields on the response and inside JWT claims. Backend access tokens contain `sub` and `sid`, so `updateUserInfo` would not reconstruct a CreatorHub user correctly.

Replace the documents and domain types together. Generate operation types from the backend schema, and validate documents in continuous integration. GraphQL Code Generator supports typed documents for Apollo: https://the-guild.dev/graphql/codegen/plugins/presets/preset-client.

### P1: Passwords are visible and written to the console

`pages/account/join.tsx:100` uses `type="text"` for the password. Lines 45, 55, and 64 log the input object, including the password. `apollo/client.ts:39` logs operations, which can include sensitive variables.

Use a password field with an explicit reveal control, remove credential/operation payload logging, add proper labels and autocomplete, and prevent duplicate submissions. Do this before using real accounts.

### P1: Sessions and account restoration are unfinished

`apollo/client.ts:19` always reports a valid token and its refresh function returns null. The 401 handler is empty. `libs/auth/index.ts` stores the access token in localStorage, decodes it without checking account/session validity, and logs out only in the browser. Its error handler assumes `graphQLErrors[0]` exists, so a network failure can cause a second exception. Login failure also calls a full-page reload, which can interrupt useful error feedback.

CreatorHub access tokens expire after 15 minutes and refresh tokens rotate. Build a session provider with a loading state, fetch the current user through `me`, serialize refresh attempts, use the rotated refresh token, call backend logout, and clear private Apollo state on logout. Private-page guards must wait for session restoration. The current `/mypage` guard checks the initially empty user immediately, so refreshing a signed-in page risks a premature redirect.

I recommend a same-origin Next.js server layer that retains tokens behind secure HttpOnly cookies and forwards Bearer credentials to NestJS. This is an integration addition, not behavior already supported by the browser-facing backend. Cookie authentication needs appropriate CSRF protections. OWASP advises against storing session identifiers in localStorage: https://cheatsheetseries.owasp.org/cheatsheets/HTML5_Security_Cheat_Sheet.html.

### P1: Visible controls do not complete their actions

Examples include `MyProfile.tsx:77`, `AddNewProperty.tsx:118`, `MyProperties.tsx:33`, community comment handlers, follow handlers, and `Chat.tsx:79`. Several lists have no data requests at all, including favorites and agent detail. This explains why a page may look complete while Save, Publish, Follow, or Send does nothing.

Track each CreatorHub action through input, mutation, loading, success, failure, and refreshed data. Avoid spending time completing Nestar-specific property or community actions that the migration will remove.

### P1: Mobile task completion is missing

Login, property search, agent search, profile editing, and other routes return placeholder text for mobile user agents. `useDeviceDetect` starts as desktop and uses user-agent detection. The desktop `.container` in `scss/app.scss:57` has a fixed 1,300px width, which caused the narrow-viewport overflow observed in the browser.

Use a single responsive component tree with CSS breakpoints and bounded fluid containers. Build login, search, profile viewing, and inquiry composition for phones as part of each feature, rather than as a later duplicate implementation.

### P1: Upload contracts do not match

`MyProfile.tsx:41` and `AddNewProperty.tsx:58` post multipart GraphQL uploads to `imageUploader` and `imagesUploader`. CreatorHub has neither operation. Its media policy accepts URLs under a configured storage root and the authenticated user's path; it does not upload bytes.

Choose storage and implement authenticated upload authorization, file validation, progress, retry, and URL submission. Preserve media alt text and ordering. Do not prefix a complete CreatorHub CDN URL with the API host as the current image components do.

The current multiple-upload code also always maps five files, even when fewer files are selected. Generate mappings from actual selected files if this code is retained during transition.

### P2: Loading and failure states can look like empty data

`TrendProperties.tsx` reads loading/error values but renders its initially empty array as "Trends Empty". A failed API request can look like a successful search with no results. Similar patterns appear elsewhere.

Give loading, no results, unavailable/private content, and network failure different messages. Offer retry for failures and filter reset for empty searches. Use query data directly when possible instead of duplicating it in component state through callbacks.

### P2: Render-time side effects and localization bugs

`Top.tsx:138` attaches a scroll listener during every render and never removes it. Move subscription setup and cleanup into an effect. `AddNewProperty.tsx:122` navigates during rendering. `LayoutBasic.tsx` sets state inside `useMemo`; derive the value instead.

The Korean flag has `id="uz"` at `Top.tsx:265`, while configured locales are en, kr, and ru. Clicking the nested flag can request the wrong locale and its handler can bubble to the menu item. Pass the intended locale explicitly. Map frontend locale identifiers deliberately to the backend's locale enum.

### P2: Accessibility and first-load cost need deliberate work

Login inputs use adjacent spans rather than associated labels. Chat icon buttons lack accessible names. Some custom clickable elements lack keyboard semantics. The frontend has little reduced-motion handling, and the WebGL homepage gallery is loaded as a core homepage dependency.

Use semantic buttons and navigation, associated labels, visible focus states, useful image descriptions, and announcements for async actions. Prioritize a lightweight portfolio-led homepage. Keep WebGL only if it helps visitors evaluate creator work, and load it separately with an alternative for devices or visitors that cannot use it. The 75 MB public directory is an asset-maintenance observation, not a claim that every asset downloads on first load.

## How the product should change

| Nestar concept | CreatorHub destination | Integration implication |
| --- | --- | --- |
| Agents | Creator discovery and public creator profile | A creator profile extends an account; use creator ID for follows and inquiries. |
| Property gallery/details | Portfolio project gallery/details | Work samples have media, categories, tags, likes, saves, and comments. They have no price. |
| Property pricing | Separate service offerings | Support fixed/starting prices and custom quotes. Unknown custom-quote prices must remain unknown. |
| My Page | Account settings and creator workspace | Separate personal identity settings, public profile, project drafts, and service drafts. |
| Favorites | Private saved projects | Hidden saved work may return an unavailable placeholder. |
| Online chat / CS inquiry | Participant-only inquiry inbox | Implement drafts, review, submit, reply, history, and terminal states. |
| Notification icon | Notification list and unread count | Connect the backend queries; initially poll, with slower polling when the page is inactive. |
| Community, property rankings, FAQ/notice admin | Defer or replace | These Nestar APIs are absent. Do not promise backend-powered features that do not exist. |

CreatorHub is a portfolio discovery and inquiry product in this backend version. Payments, checkout, escrow, ratings, general community boards, and booking are not implemented. A "Send inquiry" action fits the current product better than a "Buy now" action.

Inquiry implementation must use the latest `expectedVersion` and preserve a `clientMessageKey` UUID when retrying the same message. A version conflict needs a reload and reconciliation, not blind repetition. Disable replies after closure, cancellation, or decline. Keep account user IDs and creator-profile IDs distinct.

Public creator and project pages should render meaningful content on the server, with descriptive metadata and share images. Current static props supply translations only, while content loads in the browser. `createIsomorphicLink` also creates no HTTP link on the server, so a server rendering strategy needs client changes.

## AI assistant recommendation

Start with assisted discovery, because the backend already implements `discoverCreators(input: { request })`.

Example visitor request: "Find a remote brand designer in Seoul under 1,000,000 KRW."

The intended path is:

1. The visitor enters a request in a search assistant beside ordinary search filters.
2. The frontend calls CreatorHub's discovery query.
3. The backend calls a private AI adapter through `DISCOVERY_PARSER_URL` and `DISCOVERY_PARSER_TOKEN`.
4. The adapter uses a model to return supported structured filters only.
5. The backend validates those filters and searches published content itself.
6. The frontend presents real creator, portfolio, and service cards, with links to their pages.
7. The visitor chooses a creator and reviews an inquiry before submitting it.

The assistant should be available to visitors before sign-in. Sign-in is required when they act on protected features. Give it clear suggestions, a pending state, retry, and ordinary search as an alternative. Provider credentials stay on the server.

The existing endpoint is a single-request structured search, not a full conversational chatbot. It returns a fixed explanation and results, does not persist chat history, and does not expose extracted filters in the response. Follow-up questions, editable applied-filter chips, conversational explanations, and inquiry-draft assistance need deliberate API/UI additions. The frontend must not guess which filters the backend applied.

Without the configured adapter, the backend reports `mode: KEYWORD`. Its keyword parser recognizes some category/city/remote terms, but does not parse the numeric budget in the example. Do not label that fallback as AI or imply a budget constraint was applied. A configured adapter failure currently fails the request rather than silently falling back; present a recoverable error.

Use a provider's schema-constrained output support, then retain backend validation. Google's official documentation gives one example of this capability: https://ai.google.dev/gemini-api/docs/structured-output. Provider choice should follow a small Korean/English evaluation of taxonomy matching, budget extraction, latency, and cost. No specific provider is required by the current backend.

Keep this search assistant separate from the private inquiry inbox. Do not send private conversations, login identifiers, saved lists, or tokens to the discovery provider. Do not allow model output to invent creators, guarantee availability, change prices, or submit inquiries.

Later, add optional help drafting a project brief and answering documented site questions. Treat generated briefs as editable text that the visitor reviews. That is a new feature, not something the current discovery endpoint already does.

## Proposed implementation order

1. Create a separate `creatorhub-frontend` workspace from this starter, preserve Nestar, and add a schema-validated Apollo integration. Align tooling and remove exposed credential logging. Add session restoration, refresh, backend logout, and responsive email login, verification, and password reset.
2. Build one complete path: browse creators, open a profile, inspect projects/services, create and review an inquiry, submit it, and read/reply in the participant inbox.
3. Build the creator workspace with profile publishing, separate project/service drafts, and authenticated media uploads.
4. Connect saves, follows, comments, notifications, and account identity management. Add social login only for configured providers and implement browser-bound authorization state and callbacks.
5. Add assisted discovery with truthful AI/keyword modes, real result cards, recovery behavior, and provider evaluation. Finish visual design, accessibility, metadata, and performance verification.

Validate schema compatibility continuously. Add focused tests for expiry/refresh races, protected-page restoration, unauthorized inquiry access, message retry deduplication, version conflicts, and the complete mobile inquiry path. Do not fill the project with tests that only repeat component markup.

Upgrade the existing framework/toolchain in a controlled pass. Next.js publishes version-specific migration guidance: https://nextjs.org/docs/app/guides/upgrading. Audit actual imports before removing the redundant styling, date, icon, Create React App, upload, and legacy subscription dependencies. No subscriptions are exposed by the current CreatorHub schema, so polling is the initial match for inbox and notifications.

## Edit boundary

No project code was changed. The frontend's `AGENTS.md` says to explain fixes and obtain approval before code edits. This document is the review deliverable, not approval to execute the migration. External adapters and storage still need selection/configuration, and neither repository is proven deployed by this review.
