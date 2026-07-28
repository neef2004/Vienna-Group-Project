import { Link } from "react-router-dom";

type LegalPageProps = {
  page: "privacy" | "imprint" | "terms";
};

const operatorPlaceholder = "Team 1 GMU Vienna Study Abroad";
const emailPlaceholder = "hahadi@gmu.edu";

function PrivacyNotice() {
  return (
    <>
      <h1>Privacy notice</h1>
      <p className="legal-updated">Last updated: 28 July 2026</p>

      <h2>Who is responsible for your data?</h2>
      <p>
        The controller responsible for itineFairy is {operatorPlaceholder}.
        Contact: {emailPlaceholder}.
      </p>

      <h2>What we process and why</h2>
      <ul>
        <li>
          <strong>Account data:</strong> your email address, password hash and
          authentication details, to create and secure your account.
        </li>
        <li>
          <strong>Trip content:</strong> trips, itinerary events, dates,
          timezones and reminders, to provide the planning service you request.
        </li>
        <li>
          <strong>Collaboration data:</strong> account email addresses,
          invitations and permission levels, to let users plan trips together.
        </li>
        <li>
          <strong>Technical data:</strong> login information stored in your
          browser and server/security logs, as needed to operate and protect the
          service.
        </li>
      </ul>
      <p>
        The main legal basis is Article 6(1)(b) GDPR, because this processing is
        necessary to provide the service. Security logging may also rely on our
        legitimate interest in operating a secure service under Article 6(1)(f)
        GDPR.
      </p>

      <h2>Sharing and international transfers</h2>
      <p>
        Trip data and account email addresses may be visible to collaborators
        you invite. Data may also be processed by the service&apos;s hosting and
        infrastructure providers.
      </p>

      <h2>How long we keep data</h2>
      <p>
        Data retention periods will be decided before official release.
        Data should be deleted or anonymised when it is no longer needed,
        unless the law requires longer storage.
      </p>

      <h2>Your rights</h2>
      <p>
        Subject to the GDPR&apos;s conditions, you may request access,
        correction, deletion, restriction or portability of your data, and may
        object to processing based on legitimate interests. You may also lodge a
        complaint with the Austrian Data Protection Authority at{" "}
        <a href="https://www.dsb.gv.at/" rel="noreferrer">
          dsb.gv.at
        </a>
        .
      </p>

      <h2>Cookies and browser storage</h2>
      <p>
        itineFairy currently uses browser storage for authentication and service
        functionality. It does not currently use advertising or analytics
        cookies. If optional tracking is introduced, this notice and the consent
        controls will be updated before that tracking is activated.
      </p>
    </>
  );
}

function ImprintNotice() {
  return (
    <>
      <h1>Imprint</h1>
      <p className="legal-updated">
        Information about the service provider and media owner
      </p>

      <h2>Service provider</h2>
      <p>{operatorPlaceholder}</p>

      <h2>Contact</h2>
      <p>Email: {emailPlaceholder}</p>

      <h2>Business information</h2>
      <p>
        We are currently not registered with any courts and do not have any subsequent credentials as
        this is just an example for a school project and is not publically available.
      </p>

      <h2>Media owner and editorial responsibility</h2>
      <p>
        Media owner: {operatorPlaceholder}. Planned business purpose: provision of a
        collaborative digital itinerary-planning service. Editorial
        responsibility: Hanif Ahadi, Tasnim Abdi, Yafet Yonas, Ameerah Aguilar.
      </p>
    </>
  );
}

function TermsNotice() {
  return (
    <>
      <h1>Terms of use</h1>
      <p className="legal-updated">Last updated: 28 July 2026</p>

      <h2>The service</h2>
      <p>
        itineFairy is a planning tool that lets users create and share trip
        itineraries. Users are responsible for the content they add and for
        choosing who may access or edit a shared trip.
      </p>

      <h2>Travel information</h2>
      <p>
        Itineraries are planning aids, not professional travel, legal, medical
        or safety advice. Before travelling, verify opening hours, reservations,
        prices, transport schedules, entry requirements, accessibility and
        official safety information with the relevant provider or public
        authority.
      </p>

      <h2>Accounts and acceptable use</h2>
      <p>
        Keep your account credentials secure. Do not use the service unlawfully,
        interfere with its operation, attempt unauthorised access, or upload
        content that infringes another person&apos;s rights.
      </p>

      <h2>Availability and liability</h2>
      <p>
        The service may change or occasionally be unavailable. Nothing in these
        terms excludes liability that cannot lawfully be excluded or limits
        mandatory rights available to consumers under applicable law.
      </p>

      <h2>Operator and applicable terms</h2>
      <p>
        The service is provided by {operatorPlaceholder}. We do not offer a paid or production service yet
        but plan to implement rules for termination, governing law, dispute resolution and any consumer-specific information.
      </p>
    </>
  );
}

function LegalPage({ page }: LegalPageProps) {
  return (
    <main className="legal-page">
      <div className="legal-card">
        <Link className="legal-back-link" to="/">
          ← Back to itineFairy
        </Link>
        {page === "privacy" && <PrivacyNotice />}
        {page === "imprint" && <ImprintNotice />}
        {page === "terms" && <TermsNotice />}
      </div>
    </main>
  );
}

export default LegalPage;
