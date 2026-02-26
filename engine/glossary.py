"""
Legal Glossary Module for LexTransition AI

Provides a searchable database of legal terms, Latin maxims, and procedural terms
used in Indian law. Helps non-lawyers understand legal documents better.

Features:
- SQLite-backed term storage
- Search with autocomplete
- A-Z alphabetical filtering
- Category-based filtering
- Related sections and examples
"""

import sqlite3
import os
import re
from typing import Dict, List, Optional, Tuple

# Database file path
_base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_GLOSSARY_DB_FILE = os.path.join(_base_dir, "glossary_db.sqlite")


def get_db_connection():
    """Get a database connection for the glossary."""
    return sqlite3.connect(_GLOSSARY_DB_FILE)


def initialize_glossary_db():
    """Initialize the glossary database and create tables."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create glossary terms table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS glossary_terms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            term TEXT UNIQUE NOT NULL,
            definition TEXT NOT NULL,
            related_sections TEXT,
            examples TEXT,
            category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create index for faster searches
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_term ON glossary_terms(term)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_category ON glossary_terms(category)
    ''')
    
    conn.commit()
    conn.close()


def seed_glossary_terms():
    """Seed the database with initial legal terms if empty."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if already seeded
    cursor.execute("SELECT COUNT(*) FROM glossary_terms")
    count = cursor.fetchone()[0]
    
    if count > 0:
        conn.close()
        return
    
    # Pre-populated legal terms
    legal_terms = [
        # A
        ("Ab initio", "From the beginning; from the start. Used to describe something that exists or is valid from the very start.", "", "The contract was void ab initio.", "Latin Maxim"),
        ("Absolute Liability", "Liability without fault; strict liability where the defendant is responsible regardless of negligence or intent.", "BNS Section 106", "In M.C. Mehta v. Union of India, the Supreme Court established the principle of absolute liability for hazardous industries.", "Legal Doctrine"),
        ("Abatement", "The reduction, decrease, or cessation of something; in legal terms, the termination or suspension of a legal action.", "CPC Order 23", "The appeal abated due to the death of the appellant.", "Procedural Law"),
        ("Abduction", "The unlawful taking away or kidnapping of a person.", "BNS Section 137", "The accused was charged with abduction of the minor.", "Criminal Law"),
        ("Abetment", "The act of encouraging or assisting someone to commit a crime.", "BNS Section 44", "He was charged with abetment to suicide.", "Criminal Law"),
        ("Acquittal", "A judgment of not guilty in a criminal case; the release of a person from a criminal charge.", "CrPC Section 248", "The accused was granted acquittal for lack of evidence.", "Criminal Law"),
        ("Actus Reus", "The guilty act; the physical element of a crime that must be proven for conviction.", "General", "The actus reus of theft is the taking of another person's property.", "Legal Doctrine"),
        ("Ad litem", "For the lawsuit; appointed for the purposes of a specific legal proceeding.", "CPC Order 32", "A guardian ad litem was appointed for the minor.", "Procedural Law"),
        ("Ad valorem", "According to value; a tax or duty charged based on the value of goods.", "Customs Act Section 3", "The import duty was charged on an ad valorem basis.", "Tax Law"),
        ("Adjournment", "The postponement of a court hearing to a later date.", "CrPC Section 164", "The case was adjourned to the next week.", "Procedural Law"),
        ("Adoption", "The legal process of taking a child as one's own offspring.", "Hindu Adoptions and Maintenance Act Section 5", "The couple filed for adoption of the orphan child.", "Family Law"),
        ("Adverse Possession", "The occupation of land to which another person has title with the intention of claiming ownership.", "Limitation Act Section 5", "He claimed ownership by adverse possession for 30 years.", "Property Law"),
        ("Affidavit", "A written statement confirmed by oath for use as evidence in court.", "Evidence Act Section 3", "The witness submitted an affidavit stating the facts.", "Evidence Law"),
        ("Alibi", "A defense that the accused was elsewhere at the time a crime was committed.", "General", "The accused pleaded alibi claiming he was in another city.", "Criminal Law"),
        ("Allegation", "A claim or assertion made by a party in a legal proceeding.", "CPC Order 6", "The plaintiff made allegations of fraud.", "Procedural Law"),
        ("Amicus Curiae", "A friend of the court; a person or organization that offers information to assist the court.", "General", "The Supreme Court appointed an amicus curiae in the case.", "Procedural Law"),
        ("Anticipatory Bail", "Bail granted in anticipation of arrest; protection from arrest before it happens.", "CrPC Section 438", "The accused sought anticipatory bail from the High Court.", "Criminal Procedure"),
        ("Appeal", "A petition to a higher court to review the decision of a lower court.", "CPC Order 41", "The defendant filed an appeal against the judgment.", "Procedural Law"),
        ("Arbitration", "A method of alternative dispute resolution where a neutral third party makes a binding decision.", "Arbitration and Conciliation Act Section 7", "The dispute was referred to arbitration.", "Alternative Dispute Resolution"),
        ("Arrest", "The act of taking a person into custody for committing a crime.", "CrPC Section 41", "The police arrested the accused without warrant.", "Criminal Procedure"),
        ("Assault", "The act of causing apprehension of harmful or offensive contact.", "BNS Section 127", "He was charged with assault under Section 127.", "Criminal Law"),
        ("Audi alteram partem", "Hear the other side; the principle that no person should be condemned without being heard.", "Constitution Article 14", "The principle of audi alteram partem is fundamental to natural justice.", "Latin Maxim"),
        
        # B
        ("Bail", "The temporary release of an accused person awaiting trial, with security for appearance.", "CrPC Section 436", "The accused was granted bail on personal bond.", "Criminal Procedure"),
        ("Bailable Offense", "An offense for which bail is available as a matter of right.", "CrPC Section 2(a)", "All bailable offenses allow for automatic release on bail.", "Criminal Procedure"),
        ("Bench", "The seat where judges sit in court; also refers to the judges collectively.", "General", "The matter was heard by a full bench of the High Court.", "Court Structure"),
        ("Beneficiary", "A person who benefits from a trust, will, or insurance policy.", "Indian Trust Act Section 3", "The children were named as beneficiaries.", "Trust Law"),
        ("Bigamy", "The offense of marrying someone while already legally married to another.", "BNS Section 124", "He was charged with bigamy for having two wives.", "Criminal Law"),
        ("Bill of Exchange", "A written order to pay a sum of money to a specified person.", "Negotiable Instruments Act Section 5", "The drawer issued a bill of exchange.", "Commercial Law"),
        ("Bona fide", "In good faith; genuine and without fraud.", "General", "He is a bona fide purchaser of the property.", "Latin Maxim"),
        ("Breach of Contract", "Violation of a contractual obligation by one party.", "Indian Contract Act Section 39", "The company sued for breach of contract.", "Contract Law"),
        ("Burden of Proof", "The obligation to prove allegations in a case.", "Evidence Act Section 101", "The burden of proof lies on the prosecution.", "Evidence Law"),
        
        # C
        ("Causation", "The relationship between an act and its consequence; cause and effect.", "General", "The prosecution must prove causation.", "Legal Doctrine"),
        ("Certiorari", "A writ seeking judicial review of a lower court decision.", "Constitution Article 32, CrPC Section 401", "The High Court issued certiorari to quash the order.", "Writ Law"),
        ("Charge Sheet", "A formal police report charging a person with a crime.", "CrPC Section 173", "The police filed a charge sheet in court.", "Criminal Procedure"),
        ("Cheating", "The offense of deceiving someone to cause them to suffer loss.", "BNS Section 318", "He was charged with cheating and fraud.", "Criminal Law"),
        ("Circumstantial Evidence", "Evidence that relies on inference to establish a fact.", "Evidence Act", "The case was built on circumstantial evidence.", "Evidence Law"),
        ("Cognizable Offense", "An offense where police can arrest without a warrant.", "CrPC Section 2(c)", "Murder is a cognizable offense.", "Criminal Procedure"),
        ("Compensation", "Money paid to make up for loss or injury.", "Land Acquisition Act Section 4", "The farmer received compensation for his land.", "Property Law"),
        ("Compoundable Offense", "An offense that can be settled by the parties with permission of the court.", "BNS Section 255", "The parties opted for compounding of the offense.", "Criminal Law"),
        ("Conciliation", "A dispute resolution process using a neutral third party.", "Industrial Disputes Act", "The dispute was referred to conciliation.", "ADR"),
        ("Concurrent Sentences", "Sentences served at the same time rather than sequentially.", "General", "He received concurrent sentences of 5 years each.", "Criminal Law"),
        ("Confession", "An admission of guilt by an accused person.", "Evidence Act Section 24", "The confession was retracted by the accused.", "Evidence Law"),
        ("Consent", "Voluntary agreement or permission.", "Indian Contract Act Section 13", "The contract was voidable due to undue influence.", "Contract Law"),
        ("Consideration", "Something of value exchanged in a contract.", "Indian Contract Act Section 2(d)", "The contract lacked valid consideration.", "Contract Law"),
        ("Conspiracy", "An agreement between two or more persons to commit a crime.", "BNS Section 61", "They were charged with conspiracy to murder.", "Criminal Law"),
        ("Contempt of Court", "Disrespect or disobedience to a court.", "Contempt of Courts Act", "The witness was held in contempt of court.", "Procedural Law"),
        ("Contract", "A legally binding agreement between parties.", "Indian Contract Act Section 2(h)", "The parties entered into a contract.", "Contract Law"),
        ("Contributory Negligence", "Partial fault of the plaintiff in causing damage.", "General", "The court applied contributory negligence.", "Tort Law"),
        ("Conviction", "A judgment of guilt in a criminal case.", "CrPC Section 229", "The accused faced conviction for murder.", "Criminal Law"),
        ("Corroboration", "Supporting evidence that confirms testimony.", "Evidence Act Section 3", "The witness needed corroboration.", "Evidence Law"),
        ("Criminal Intimidation", "Threatening a person to cause death or injury.", "BNS Section 140", "He was charged with criminal intimidation.", "Criminal Law"),
        ("Cross-examination", "Questioning a witness by the opposing party.", "Evidence Act Section 137", "The witness was subjected to cross-examination.", "Evidence Law"),
        ("Culpable Homicide", "The act of causing death with knowledge or intention.", "BNS Section 299", "The accused was charged with culpable homicide.", "Criminal Law"),
        ("Custody", "The detention or control of a person or property.", "CrPC Section 46", "The child was handed over to police custody.", "Criminal Procedure"),
        
        # D
        ("Damages", "Monetary compensation for loss or injury.", "General", "She was awarded damages of Rs. 5 lakhs.", "Tort Law"),
        ("Decree", "A formal court order deciding a case.", "CPC Order 20", "The decree was passed in favor of the plaintiff.", "Civil Procedure"),
        ("Deed", "A legal document signed and delivered.", "Transfer of Property Act", "The deed was registered with the sub-registrar.", "Property Law"),
        ("Defamation", "The offense of making false statements harming reputation.", "BNS Section 298", "He sued for defamation.", "Criminal Law"),
        ("Default", "Failure to fulfill an obligation.", "General", "The borrower defaulted on the loan.", "Contract Law"),
        ("Defense", "The case presented by an accused to contest allegations.", "General", "The defense presented an alibi.", "Legal Practice"),
        ("De novo", "Anew; starting fresh.", "General", "The case was remanded for de novo trial.", "Latin Maxim"),
        ("Deposition", "Sworn testimony of a witness taken outside court.", "CPC Order 18", "The deposition was recorded on video.", "Evidence Law"),
        ("Desertion", "The act of abandoning a person or obligation.", "Hindu Marriage Act Section 10", "Wife filed for divorce on grounds of desertion.", "Family Law"),
        ("Detention", "The state of being held in custody.", "CrPC Section 167", "The accused was under police detention.", "Criminal Procedure"),
        ("Dictum", "A statement in a judgment that is not essential to the decision.", "General", "The observation was obiter dictum.", "Legal Writing"),
        ("Direct Evidence", "Evidence that directly proves a fact without inference.", "Evidence Act", "The CCTV footage was direct evidence.", "Evidence Law"),
        ("Discovery", "The pre-trial process of obtaining evidence.", "CPC Order 11", "The plaintiff sought discovery of documents.", "Civil Procedure"),
        ("Dismissal", "The rejection of a case or termination of employment.", "CPC Order 41", "The suit was dismissed for non-prosecution.", "Procedural Law"),
        ("Divorce", "Legal dissolution of marriage.", "Hindu Marriage Act Section 13", "The wife filed for divorce.", "Family Law"),
        ("Document", "A written or electronic record with legal significance.", "Evidence Act Section 3", "The sale deed is an important document.", "Evidence Law"),
        ("Domestic Violence", "Violence within a domestic setting.", "Protection of Women from Domestic Violence Act", "The victim sought relief under DV Act.", "Family Law"),
        ("Double Jeopardy", "Being tried twice for the same offense.", "Constitution Article 20(2)", "The plea of double jeopardy was accepted.", "Constitutional Law"),
        ("Due Process", "Fair treatment through the legal system.", "Constitution Article 21", "The principle of due process was followed.", "Constitutional Law"),
        ("Dying Declaration", "Statement made by a person about to die.", "Evidence Act Section 32", "The dying declaration was recorded.", "Evidence Law"),
        
        # E
        ("Easement", "A right to use another's land for a specific purpose.", "Indian Easements Act Section 4", "He had an easement of pathway over neighbor's land.", "Property Law"),
        ("Ejusdem Generis", "Of the same kind; interpreting general words with specific ones.", "General", "The rule of ejusdem generis was applied.", "Latin Maxim"),
        ("Embezzlement", "Theft of funds by a person entrusted with them.", "BNS Section 316", "The accountant was charged with embezzlement.", "Criminal Law"),
        ("Encroachment", "Unauthorized intrusion on another's property.", "General", "The encroachment was removed by police.", "Property Law"),
        ("Endorsement", "A signature on a document; support for something.", "Negotiable Instruments Act", "The check had a restrictive endorsement.", "Commercial Law"),
        ("Equity", "Fairness; a system of law supplementing common law.", "General", "Equity intervenes where law is silent.", "Legal System"),
        ("Escheat", "Property reverting to the state when there are no heirs.", "General", "The property escheated to the government.", "Property Law"),
        ("Escrow", "Money or property held by a third party until conditions are met.", "General", "The funds were held in escrow.", "Contract Law"),
        ("Estate", "Property; the total property owned by a person.", "General", "The estate was distributed among heirs.", "Property Law"),
        ("Estoppel", "A principle preventing denial of established facts.", "Evidence Act Section 115", "The doctrine of estoppel applied.", "Legal Doctrine"),
        ("Evidence", "Any material or information presented to prove facts.", "Evidence Act Section 3", "The evidence was circumstantial.", "Evidence Law"),
        ("Ex parte", "With only one party present.", "CPC Order 39", "The court granted ex parte injunction.", "Latin Maxim"),
        ("Executor", "A person appointed to carry out a will.", "Indian Succession Act Section 2", "The executor distributed the estate.", "Property Law"),
        ("Extortion", "Obtaining property by threat.", "BNS Section 307", "He was charged with extortion.", "Criminal Law"),
        
        # F
        ("Fabrication", "The act of making up false evidence.", "BNS Section 192", "He was charged with fabrication of evidence.", "Criminal Law"),
        ("Fait accompli", "An accomplished fact; something already done.", "General", "The occupation was a fait accompli.", "Latin Maxim"),
        ("False Imprisonment", "Unlawful detention of a person.", "BNS Section 128", "He sued for false imprisonment.", "Criminal Law"),
        ("Fee Simple", "Absolute ownership of property.", "Transfer of Property Act", "The property was held in fee simple.", "Property Law"),
        ("Fiduciary", "A person in a position of trust.", "Indian Trust Act", "A trustee is a fiduciary.", "Trust Law"),
        ("First Information Report", "The first report of a crime to police.", "CrPC Section 154", "The FIR was registered at the police station.", "Criminal Procedure"),
        ("Force Majeure", "Unforeseeable circumstances preventing contract performance.", "Indian Contract Act Section 32", "The contract was terminated due to force majeure.", "Contract Law"),
        ("Forensic Evidence", "Evidence obtained through scientific testing.", "Evidence Act Section 45", "Forensic evidence proved his innocence.", "Evidence Law"),
        ("Forfeiture", "Loss of property or rights as penalty.", "General", "The property was subject to forfeiture.", "Legal Doctrine"),
        ("Forgery", "The crime of making a false document.", "BNS Section 319", "He was charged with forgery.", "Criminal Law"),
        ("Fraud", "Deceitful conduct for gain.", "BNS Section 318", "The company was accused of fraud.", "Criminal Law"),
        ("Freedom of Speech", "The right to express opinions.", "Constitution Article 19(1)(a)", "Freedom of speech is a fundamental right.", "Constitutional Law"),
        ("Fundamental Rights", "Basic human rights guaranteed by the Constitution.", "Constitution Part III", "Right to equality is a fundamental right.", "Constitutional Law"),
        
        # G
        ("Gift", "Transfer of property without consideration.", "Transfer of Property Act Section 122", "The property was gifted to the son.", "Property Law"),
        ("Good Faith", "Honesty and fairness in dealing.", "Indian Contract Act Section 17", "The transaction was in good faith.", "Contract Law"),
        ("Guarantee", "A promise to fulfill another's obligation.", "Indian Contract Act Section 126", "He stood guarantee for the loan.", "Contract Law"),
        ("Guardian", "A person who protects another.", "Guardian and Wards Act", "A guardian was appointed for the minor.", "Family Law"),
        
        # H
        ("Habeas Corpus", "A writ requiring a person to be brought before a court.", "Constitution Article 32, 226", "Habeas corpus was filed for illegal detention.", "Writ Law"),
        ("Harassment", "Persistent annoyance or intimidation.", "BNS Section 131", "She filed complaint for harassment.", "Criminal Law"),
        ("Hearsay Evidence", "Evidence of what someone else said, not what they personally observed.", "Evidence Act", "Hearsay evidence is generally not admissible.", "Evidence Law"),
        ("Holding", "The legal principle established in a court's judgment.", "General", "The holding of the case is binding.", "Legal Writing"),
        
        # I
        ("Idemnity", "A promise to compensate for loss or damage.", "Indian Contract Act Section 124", "The indemnity clause protected the seller.", "Contract Law"),
        ("Indictment", "A formal accusation charging a person with a crime.", "CrPC Section 240", "The grand jury issued an indictment.", "Criminal Procedure"),
        ("Infant", "A person under 18 years of age.", "General", "An infant cannot enter into a contract.", "Legal Term"),
        ("Injunction", "A court order requiring a party to do or refrain from doing something.", "CPC Order 39", "The court granted a temporary injunction.", "Civil Procedure"),
        ("Inquest", "A judicial inquiry into a death.", "CrPC Section 174", "The coroner held an inquest.", "Criminal Procedure"),
        ("Insolvency", "The state of being unable to pay debts.", "Insolvency and Bankruptcy Code", "The debtor declared insolvency.", "Banking Law"),
        ("Interim Order", "A temporary order passed until the final decision.", "CPC Order 39", "The court passed an interim order.", "Procedural Law"),
        ("Interrogatories", "Written questions asked to a party in a lawsuit.", "CPC Order 11", "The plaintiff served interrogatories.", "Civil Procedure"),
        ("Intimidation", "The act of making someone fearful.", "BNS Section 140", "He was charged with criminal intimidation.", "Criminal Law"),
        
        # J
        ("Joinder of Parties", "Adding multiple parties to a lawsuit.", "CPC Order 1", "The court ordered joinder of parties.", "Civil Procedure"),
        ("Judgment", "The official decision of a court.", "CPC Order 20", "The judgment was pronounced.", "Civil Procedure"),
        ("Judicial Review", "The power of courts to examine government actions.", "Constitution Article 32, 226", "The Supreme Court exercised judicial review.", "Constitutional Law"),
        ("Jurisdiction", "The authority of a court to hear and decide cases.", "General", "The High Court has jurisdiction over the matter.", "Court Structure"),
        ("Jury", "A group of citizens sworn to deliver a verdict.", "General", "The jury found the accused guilty.", "Court Structure"),
        
        # L
        ("Laches", "Unreasonable delay in asserting a right.", "General", "The claim was dismissed for laches.", "Legal Doctrine"),
        ("Landmark Judgment", "A court decision that establishes an important precedent.", "General", "The Kesavananda Bharati case is a landmark judgment.", "Legal Writing"),
        ("Leading Question", "A question that suggests the desired answer.", "Evidence Act Section 141", "The advocate was not allowed to ask leading questions.", "Evidence Law"),
        ("Lease", "A contract granting the right to use property for a period.", "Transfer of Property Act", "The lease was for 5 years.", "Property Law"),
        ("Legal Heir", "A person entitled to inherit property by law.", "General", "The legal heirs filed the claim.", "Property Law"),
        ("Letter of Credit", "A bank guarantee for payment.", "General", "The letter of credit was issued.", "Commercial Law"),
        ("Libel", "Defamation in written form.", "BNS Section 298", "He sued for libel.", "Criminal Law"),
        ("Lien", "A right to keep possession of property until a debt is paid.", "General", "The banker had a lien on the documents.", "Property Law"),
        ("Limitation Period", "The time within which a lawsuit must be filed.", "Limitation Act", "The limitation period had expired.", "Procedural Law"),
        ("Litigation", "The process of taking legal action through courts.", "General", "Litigation is expensive.", "Legal Practice"),
        ("Locomotive", "In legal terms, the power to move or initiate action.", "General", "The court has loco parentis power.", "Legal Term"),
        ("Locus Standi", "The right to appear in court.", "General", "The petitioner lacked locus standi.", "Procedural Law"),
        
        # M
        ("Maintenance", "Financial support for a spouse or child.", "Hindu Adoption and Maintenance Act", "Wife claimed maintenance.", "Family Law"),
        ("Mandamus", "A writ commanding a person or body to perform a duty.", "Constitution Article 32", "The court issued mandamus.", "Writ Law"),
        ("Manslaughter", "The unlawful killing of a human without malice.", "BNS Section 302", "He was charged with manslaughter.", "Criminal Law"),
        ("Mens Rea", "Guilty mind; the mental element of a crime.", "General", "Mens rea is essential for criminal liability.", "Legal Doctrine"),
        ("Merits", "The substantive issues of a case.", "General", "The case was dismissed on merits.", "Legal Practice"),
        ("Minor", "A person below 18 years of age.", "General", "A minor cannot contract.", "Legal Term"),
        ("Miranda Warning", "The right to remain silent and have an attorney.", "General", "The police gave the Miranda warning.", "Criminal Procedure"),
        ("Miscarriage of Justice", "A failure to provide fair trial leading to wrong result.", "General", "The convict claimed miscarriage of justice.", "Legal Doctrine"),
        ("Misdemeanor", "A criminal offense less serious than a felony.", "General", "He was charged with a misdemeanor.", "Criminal Law"),
        ("Misrepresentation", "A false statement inducing a contract.", "Indian Contract Act Section 18", "The contract was void due to misrepresentation.", "Contract Law"),
        ("Molestation", "Wrongful sexual conduct.", "BNS Section 354", "She filed complaint for molestation.", "Criminal Law"),
        ("Mortgage", "A transfer of property as security for a loan.", "Transfer of Property Act Section 58", "The property was mortgaged.", "Property Law"),
        ("Motion", "A formal request to the court.", "CPC Order 29", "The defense filed a motion.", "Procedural Law"),
        ("Moot", "To debate or argue a hypothetical case.", "General", "The law students participated in a moot court.", "Legal Education"),
        
        # N
        ("Natural Justice", "Fair procedure including right to be heard.", "Constitution Article 14", "The principles of natural justice were followed.", "Legal Doctrine"),
        ("Negligence", "Failure to take reasonable care.", "General", "He sued for negligence.", "Tort Law"),
        ("Negotiable Instrument", "A document promising payment.", "Negotiable Instruments Act", "A check is a negotiable instrument.", "Commercial Law"),
        ("Next Friend", "A person acting on behalf of a minor.", "CPC Order 32", "A next friend filed the suit.", "Procedural Law"),
        ("Nuisance", "Unlawful interference with use of property.", "General", "The neighbor sued for nuisance.", "Tort Law"),
        
        # O
        ("Obiter Dictum", "Statements in a judgment not essential to the decision.", "General", "The observation was obiter dictum.", "Legal Writing"),
        ("Offense", "A breach of law; a crime.", "General", "Theft is an offense.", "Criminal Law"),
        ("Order", "A decision of a court or judge.", "CPC Order 43", "The court passed an order.", "Procedural Law"),
        
        # P
        ("Pardon", "Forgiveness of crime by executive authority.", "Constitution Article 72", "The President granted pardon.", "Constitutional Law"),
        ("Parol Evidence", "Oral evidence to vary a written contract.", "Evidence Act", "Parol evidence was not allowed.", "Evidence Law"),
        ("Party", "A person involved in a lawsuit.", "CPC Order 1", "All parties were present.", "Procedural Law"),
        ("Passport", "An official government document for travel.", "Passport Act", "His passport was impounded.", "Administrative Law"),
        ("Per Incuriam", "A decision made without considering relevant law.", "General", "The judgment was per incuriam.", "Legal Writing"),
        ("Perjury", "The offense of telling lies in court.", "BNS Section 191", "He was charged with perjury.", "Criminal Law"),
        ("Permutation", "Change; alteration in legal terms.", "General", "The contract allowed permutation.", "Legal Term"),
        ("Petition", "A formal written request to a court.", "General", "He filed a petition.", "Procedural Law"),
        ("Plaintiff", "A person who starts a lawsuit.", "CPC", "The plaintiff won the case.", "Civil Procedure"),
        ("Plea", "A defendant's answer to charges.", "CrPC", "The accused entered a plea of not guilty.", "Criminal Procedure"),
        ("Pleadings", "Written statements of parties in a lawsuit.", "CPC Order 6", "The pleadings were exchanged.", "Civil Procedure"),
        ("Preamble", "An introductory statement.", "Constitution", "The preamble declares India as sovereign.", "Constitutional Law"),
        ("Precedent", "A legal decision binding on future cases.", "General", "The case set a precedent.", "Legal Doctrine"),
        ("Presumption", "An assumption of fact until proven otherwise.", "Evidence Act", "The presumption of innocence applies.", "Evidence Law"),
        ("Prima Facie", "At first sight; based on first impression.", "General", "There is prima facie evidence.", "Latin Maxim"),
        ("Principal", "The person in whose behalf an agent acts.", "Indian Contract Act Section 182", "The principal was bound.", "Contract Law"),
        ("Private Complaint", "A complaint filed by an individual.", "CrPC Section 200", "She filed a private complaint.", "Criminal Procedure"),
        ("Probate", "The official proving of a will.", "Indian Succession Act", "Probate was granted.", "Property Law"),
        ("Proceeding", "Legal action in a court.", "General", "The proceeding was adjourned.", "Procedural Law"),
        ("Prosecution", "The process of bringing criminal charges.", "General", "The prosecution presented evidence.", "Criminal Procedure"),
        ("Protector", "One who protects; in law, a guardian.", "General", "The court appointed a protector.", "Legal Term"),
        ("Provisional Attachment", "Temporary seizure of property.", "CPC Order 38", "The court ordered provisional attachment.", "Civil Procedure"),
        ("Provisional Order", "A temporary order.", "General", "A provisional order was passed.", "Procedural Law"),
        ("Punishment", "The penalty for committing a crime.", "General", "The punishment was imprisonment.", "Criminal Law"),
        ("Purchaser", "One who buys.", "General", "The purchaser completed the transaction.", "Property Law"),
        
        # Q
        ("Quash", "To nullify or void.", "CrPC Section 482", "The court quashed the proceedings.", "Procedural Law"),
        ("Question of Law", "An issue about the interpretation of law.", "General", "It was a question of law.", "Legal Doctrine"),
        ("Question of Fact", "An issue about what actually happened.", "General", "The jury decided the question of fact.", "Legal Doctrine"),
        ("Quid Pro Quo", "Something given for something received.", "General", "There was no quid pro quo.", "Latin Maxim"),
        ("Quo Warranto", "A writ questioning authority to hold office.", "Constitution Article 32", "Quo warranto was issued.", "Writ Law"),
        
        # R
        ("Ratification", "Approval of an act already done.", "Indian Contract Act Section 196", "The contract was ratified.", "Contract Law"),
        ("Rebuttal", "Evidence contradicting the opposing party's case.", "Evidence Act", "The defense offered rebuttal.", "Evidence Law"),
        ("Receiver", "A person appointed to manage property.", "CPC Order 40", "A receiver was appointed.", "Civil Procedure"),
        ("Recognition", "Official acknowledgment.", "General", "The degree was given recognition.", "Legal Term"),
        ("Redress", "Remedy or compensation.", "General", "The victim sought redress.", "Legal Doctrine"),
        ("Referee", "A person appointed to decide a dispute.", "CPC Order 46", "A referee was appointed.", "Civil Procedure"),
        ("Rehearing", "A second hearing of a case.", "General", "The court ordered a rehearing.", "Procedural Law"),
        ("Relevancy", "The quality of being relevant.", "Evidence Act Section 5", "The evidence was relevant.", "Evidence Law"),
        ("Remand", "Sending a case back for further action.", "CrPC Section 397", "The accused was remanded to custody.", "Criminal Procedure"),
        ("Remedy", "The legal means of enforcing a right.", "General", "The court provided remedy.", "Legal Doctrine"),
        ("Rent", "Payment for use of property.", "General", "Rent was due.", "Property Law"),
        ("Rescission", "Cancellation of a contract.", "Indian Contract Act Section 39", "The contract was rescinded.", "Contract Law"),
        ("Residence", "The place where one lives.", "General", "The residence was in Delhi.", "Legal Term"),
        ("Respondent", "The defendant in an appeal.", "General", "The respondent appeared.", "Procedural Law"),
        ("Restitution", "Restoration of something taken.", "General", "Restitution was ordered.", "Legal Doctrine"),
        ("Retention", "The act of keeping something.", "General", "The document was under retention.", "Legal Term"),
        ("Review", "Re-examination of a case.", "CPC Order 47", "The party filed a review.", "Procedural Law"),
        ("Revocation", "The act of cancelling.", "Indian Contract Act Section 3", "The offer was subject to revocation.", "Contract Law"),
        ("Right", "A legal entitlement.", "General", "He had a right to property.", "Legal Doctrine"),
        ("Right to Information", "The right to access government information.", "RTI Act", "He filed an RTI application.", "Constitutional Law"),
        
        # S
        ("Sale", "Transfer of property for money.", "Transfer of Property Act Section 54", "The sale was completed.", "Property Law"),
        ("Sanction", "Official permission; approval.", "General", "Sanction was obtained.", "Administrative Law"),
        ("Search Warrant", "Authorization to search premises.", "CrPC Section 93", "A search warrant was issued.", "Criminal Procedure"),
        ("Second Appeal", "An appeal from a first appellate court.", "CPC Order 41", "A second appeal was filed.", "Civil Procedure"),
        ("Section", "A division of a legal document.", "General", "Under Section 302 IPC.", "Legal Writing"),
        ("Secularism", "Separation of state from religion.", "Constitution Article 25", "India follows secularism.", "Constitutional Law"),
        ("Sedition", "Inciting rebellion against the government.", "BNS Section 124", "He was charged with sedition.", "Criminal Law"),
        ("Seizure", "Taking property by legal authority.", "Customs Act", "The customs seized the goods.", "Revenue Law"),
        ("Self-Defense", "The right to protect oneself.", "General", "It was a case of self-defense.", "Criminal Law"),
        ("Sentence", "The punishment imposed by a court.", "CrPC Section 235", "The sentence was 5 years.", "Criminal Law"),
        ("Sequestration", "Taking property from a party for compliance.", "CPC Order 39", "Sequestration was ordered.", "Civil Procedure"),
        ("Service", "Delivery of legal documents.", "CPC Order 5", "Service was effected.", "Procedural Law"),
        ("Set-off", "A counterclaim reducing the plaintiff's claim.", "CPC Order 8", "A set-off was claimed.", "Civil Procedure"),
        ("Settlement", "Resolution of a dispute.", "General", "The parties reached a settlement.", "ADR"),
        ("Share", "A unit of ownership in a company.", "Companies Act", "He held 50% shares.", "Corporate Law"),
        ("Signature", "One's name written in a document.", "General", "The signature was verified.", "Evidence Law"),
        ("Slander", "Defamation by spoken words.", "BNS Section 298", "He sued for slander.", "Criminal Law"),
        ("Specific Performance", "Court order to perform a contract.", "Indian Contract Act Section 20", "Specific performance was granted.", "Contract Law"),
        ("Stalking", "Following or contacting someone repeatedly.", "BNS Section 354", "She was charged with stalking.", "Criminal Law"),
        ("Status", "Legal position or condition.", "General", "The status was changed.", "Legal Term"),
        ("Statute", "A written law passed by legislature.", "General", "The IPC is a statute.", "Legislation"),
        ("Stay", "Temporarily halting a legal proceeding.", "CPC Order 39", "The execution was stayed.", "Procedural Law"),
        ("Strict Liability", "Liability without fault.", "BNS Section 106", "The doctrine of strict liability applies.", "Legal Doctrine"),
        ("Subjudice", "Under consideration by a court.", "General", "The matter is subjudice.", "Procedural Law"),
        ("Submission", "Presenting something to a court.", "General", "The lawyer made submissions.", "Legal Practice"),
        ("Subornation", "Inducing someone to commit perjury.", "BNS Section 193", "He was charged with subornation.", "Criminal Law"),
        ("Subpoena", "A court order requiring attendance.", "Evidence Act Section 27", "A subpoena was issued.", "Evidence Law"),
        ("Suicide", "The act of killing oneself.", "BNS Section 305", "Abetment of suicide is an offense.", "Criminal Law"),
        ("Suit", "A legal action in a court.", "CPC", "He filed a suit for damages.", "Civil Procedure"),
        ("Summary Judgment", "Decision without full trial.", "CPC Order 13A", "Summary judgment was granted.", "Civil Procedure"),
        ("Summons", "A court order to appear.", "CPC Order 5", "Summons was served.", "Procedural Law"),
        ("Sunset Clause", "A provision ending a law after a date.", "General", "The sunset clause applied.", "Legal Term"),
        ("Supreme Court", "The highest court in India.", "Constitution Article 124", "The Supreme Court delivered the judgment.", "Court Structure"),
        
        # T
        ("Tax", "A compulsory payment to the government.", "Income Tax Act", "Tax was deducted at source.", "Tax Law"),
        ("Tenant", "One who occupies property.", "General", "The tenant paid rent.", "Property Law"),
        ("Tender", "An offer to perform.", "General", "Tender was invited.", "Contract Law"),
        ("Territorial Jurisdiction", "Geographic area of court's authority.", "CPC Section 20", "The territorial jurisdiction was in Delhi.", "Court Structure"),
        ("Theft", "Taking property without consent.", "BNS Section 303", "He was charged with theft.", "Criminal Law"),
        ("Title", "Legal right to property.", "Transfer of Property Act", "The title was clear.", "Property Law"),
        ("Tort", "A civil wrong.", "General", "Defamation is a tort.", "Tort Law"),
        ("Transcript", "A written record of proceedings.", "General", "The transcript was filed.", "Procedural Law"),
        ("Transfer", "Moving property from one person to another.", "Transfer of Property Act", "The transfer was registered.", "Property Law"),
        ("Travel", "In law, to range or extend.", "General", "The argument does not travel.", "Legal Term"),
        ("Trespass", "Unauthorized entry onto property.", "BNS Section 326", "He was charged with trespass.", "Criminal Law"),
        ("Trial", "A court examination of a case.", "General", "The trial was conducted.", "Procedural Law"),
        ("Tribunal", "A special court.", "General", "The tribunal passed the order.", "Court Structure"),
        ("Trust", "An arrangement where property is held for another.", "Indian Trust Act", "The trust was registered.", "Trust Law"),
        
        # U
        ("Ulta Vires", "Beyond legal authority.", "Companies Act", "The act was ultra vires.", "Corporate Law"),
        ("Undertaking", "A promise to the court.", "General", "An undertaking was given.", "Legal Practice"),
        ("Undue Influence", "Improper pressure in a contract.", "Indian Contract Act Section 16", "The contract was voidable due to undue influence.", "Contract Law"),
        ("Uniform Civil Code", "Single law for all religions.", "Constitution Article 44", "Uniform Civil Code is a directive principle.", "Constitutional Law"),
        ("Utilize", "To make use of.", "General", "The property was utilized.", "Legal Term"),
        
        # V
        ("Vacate", "To leave or set aside.", "General", "The order was vacated.", "Procedural Law"),
        ("Valid", "Legally effective.", "General", "The contract was valid.", "Contract Law"),
        ("Valuation", "Determining the worth of property.", "General", "Valuation was done.", "Property Law"),
        ("Variance", "Difference between allegations and proof.", "Evidence Act", "There was variance in evidence.", "Evidence Law"),
        ("Vendee", "One who purchases.", "General", "The vendee took possession.", "Property Law"),
        ("Vendor", "One who sells.", "General", "The vendor executed the deed.", "Property Law"),
        ("Venue", "The location of a trial.", "CPC Section 20", "The venue was changed.", "Procedural Law"),
        ("Verdict", "The decision of a jury or judge.", "General", "The verdict was guilty.", "Criminal Procedure"),
        ("Verification", "Confirmation of truth.", "CPC Order 19", "Verification was done.", "Civil Procedure"),
        ("Vicarious Liability", "Liability for another's actions.", "General", "The employer had vicarious liability.", "Tort Law"),
        ("Victim", "One who suffers harm.", "General", "The victim testified.", "Criminal Law"),
        ("View", "An inspection by the court.", "CrPC Section 310", "The court ordered a view.", "Criminal Procedure"),
        ("Vigilant", "Watchful; alert.", "General", "Vigilantibus non dormientibus jura.", "Legal Term"),
        ("Vindicate", "To clear from blame.", "General", "He was vindicated.", "Legal Doctrine"),
        ("Void", "Having no legal effect.", "Indian Contract Act Section 2(j)", "The contract was void.", "Contract Law"),
        ("Voidable", "Valid until cancelled.", "Indian Contract Act Section 2(i)", "The contract was voidable.", "Contract Law"),
        
        # W
        ("Wager", "A bet on an uncertain event.", "Indian Contract Act Section 30", "Wagering agreements are void.", "Contract Law"),
        ("Waiver", "Voluntarily giving up a right.", "General", "There was waiver of rights.", "Legal Doctrine"),
        ("Warrant", "An authorization.", "CrPC Section 70", "A warrant was issued.", "Criminal Procedure"),
        ("Waste", "Damage to property.", "General", "The tenant committed waste.", "Property Law"),
        ("Will", "A legal document of testament.", "Indian Succession Act", "The will was probated.", "Property Law"),
        ("Winding Up", "Dissolution of a company.", "Companies Act", "Winding up was ordered.", "Corporate Law"),
        ("Witness", "One who testifies.", "Evidence Act", "The witness was examined.", "Evidence Law"),
        ("Writ", "A formal court order.", "Constitution Article 32", "A writ was filed.", "Writ Law"),
        
        # Z
        ("Zero FIR", "An FIR that can be filed at any police station.", "CrPC Section 154", "A zero FIR was registered.", "Criminal Procedure"),
    ]
    
    # Insert all terms
    for term_data in legal_terms:
        try:
            cursor.execute('''
                INSERT INTO glossary_terms (term, definition, related_sections, examples, category)
                VALUES (?, ?, ?, ?, ?)
            ''', term_data)
        except sqlite3.IntegrityError:
            pass  # Skip duplicates
    
    conn.commit()
    conn.close()


# CRUD Operations

def add_term(term: str, definition: str, related_sections: str = "", 
             examples: str = "", category: str = "General") -> bool:
    """Add a new term to the glossary."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO glossary_terms (term, definition, related_sections, examples, category)
            VALUES (?, ?, ?, ?, ?)
        ''', (term, definition, related_sections, examples, category))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False
    except Exception as e:
        print(f"Error adding term: {e}")
        return False


def get_term(term: str) -> Optional[Dict]:
    """Get a specific term by name."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM glossary_terms WHERE LOWER(term) = LOWER(?)", (term,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'term': row[1],
                'definition': row[2],
                'related_sections': row[3],
                'examples': row[4],
                'category': row[5]
            }
        return None
    except Exception as e:
        print(f"Error getting term: {e}")
        return None


def search_terms(query: str, limit: int = 20) -> List[Dict]:
    """Search terms by query (partial match)."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        search_pattern = f"%{query}%"
        cursor.execute('''
            SELECT * FROM glossary_terms 
            WHERE term LIKE ? OR definition LIKE ?
            ORDER BY term
            LIMIT ?
        ''', (search_pattern, search_pattern, limit))
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': row[0],
                'term': row[1],
                'definition': row[2],
                'related_sections': row[3],
                'examples': row[4],
                'category': row[5]
            }
            for row in rows
        ]
    except Exception as e:
        print(f"Error searching terms: {e}")
        return []


def get_all_terms(limit: int = 1000) -> List[Dict]:
    """Get all terms from the glossary."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM glossary_terms ORDER BY term LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': row[0],
                'term': row[1],
                'definition': row[2],
                'related_sections': row[3],
                'examples': row[4],
                'category': row[5]
            }
            for row in rows
        ]
    except Exception as e:
        print(f"Error getting terms: {e}")
        return []


def get_terms_by_letter(letter: str) -> List[Dict]:
    """Get terms starting with a specific letter."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM glossary_terms 
            WHERE term LIKE ?
            ORDER BY term
        ''', (f"{letter}%",))
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': row[0],
                'term': row[1],
                'definition': row[2],
                'related_sections': row[3],
                'examples': row[4],
                'category': row[5]
            }
            for row in rows
        ]
    except Exception as e:
        print(f"Error getting terms by letter: {e}")
        return []


def get_terms_by_category(category: str) -> List[Dict]:
    """Get terms by category."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM glossary_terms 
            WHERE category = ?
            ORDER BY term
        ''', (category,))
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': row[0],
                'term': row[1],
                'definition': row[2],
                'related_sections': row[3],
                'examples': row[4],
                'category': row[5]
            }
            for row in rows
        ]
    except Exception as e:
        print(f"Error getting terms by category: {e}")
        return []


def get_categories() -> List[str]:
    """Get all unique categories."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT category FROM glossary_terms ORDER BY category")
        rows = cursor.fetchall()
        conn.close()
        return [row[0] for row in rows if row[0]]
    except Exception as e:
        print(f"Error getting categories: {e}")
        return []


def get_autocomplete_terms(query: str, limit: int = 10) -> List[str]:
    """Get autocomplete suggestions for terms."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        search_pattern = f"{query}%"
        cursor.execute('''
            SELECT term FROM glossary_terms 
            WHERE term LIKE ?
            ORDER BY term
            LIMIT ?
        ''', (search_pattern, limit))
        rows = cursor.fetchall()
        conn.close()
        return [row[0] for row in rows]
    except Exception as e:
        print(f"Error getting autocomplete terms: {e}")
        return []


def detect_legal_terms(text: str) -> List[Dict]:
    """Detect legal terms in a given text and return their definitions."""
    try:
        all_terms = get_all_terms()
        detected = []
        text_lower = text.lower()
        
        for term_data in all_terms:
            term_lower = term_data['term'].lower()
            # Check if term appears in text
            if term_lower in text_lower:
                detected.append(term_data)
        
        return detected
    except Exception as e:
        print(f"Error detecting legal terms: {e}")
        return []


def get_term_count() -> int:
    """Get total number of terms in glossary."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM glossary_terms")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except Exception as e:
        print(f"Error getting term count: {e}")
        return 0


def delete_term(term: str) -> bool:
    """Delete a term from the glossary."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM glossary_terms WHERE LOWER(term) = LOWER(?)", (term,))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0
    except Exception as e:
        print(f"Error deleting term: {e}")
        return False


def update_term(term: str, definition: str = None, related_sections: str = None,
                examples: str = None, category: str = None) -> bool:
    """Update an existing term."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if definition is not None:
            updates.append("definition = ?")
            params.append(definition)
        if related_sections is not None:
            updates.append("related_sections = ?")
            params.append(related_sections)
        if examples is not None:
            updates.append("examples = ?")
            params.append(examples)
        if category is not None:
            updates.append("category = ?")
            params.append(category)
        
        if not updates:
            return False
        
        params.append(term)
        query = f"UPDATE glossary_terms SET {', '.join(updates)} WHERE LOWER(term) = LOWER(?)"
        cursor.execute(query, params)
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0
    except Exception as e:
        print(f"Error updating term: {e}")
        return False


# Initialize database on import
initialize_glossary_db()
seed_glossary_terms()
