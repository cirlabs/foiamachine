from apps.government.models import Language, Nation,\
 Government, Statute, FeeExemptionOther
from apps.core.unicode_csv import UnicodeReader
from django.conf import settings

import logging

logger = logging.getLogger('default')

def get_defaults():
    language, created = Language.objects.get_or_create(name='English')
    ntn, created = Nation.objects.get_or_create(name='United States of America')
    if created:
        ntn.primary_language = language
        ntn.foi_languages = [language]
    govt, created  = Government.objects.get_or_create(name='United States of America',
        level=Government.GOV_LEVELS[2][0], nation=ntn)
    return (language, ntn, govt)

def get_or_create_us_govt(govt_name, gov_type):
    language, ntn, govt = get_defaults()
    try:
        keyvals = Government.get_us_gov_levels()
        lvl = keyvals[gov_type]
        govt, created = Government.objects.get_or_create(name=govt_name, level=lvl, nation=ntn)
        return govt
    except Exception as e:
        logger.info("could not find us government level for type %s e=%s" % (govt_name, e))
        return None

def load_states():
    language, created = Language.objects.get_or_create(name='English')
    ntn, created = Nation.objects.get_or_create(name='United States of America')
    fname = settings.SITE_ROOT + "/apps/government/data/foia_statutes.csv"
    print fname
    reader = list(UnicodeReader(open(fname, 'rb')))
    idx = 0
    for row in reader[1:]:
        loc = row[1]
        typee = row[2]
        govt = get_or_create_us_govt(loc, typee)
        print "%s %s" % (loc, idx)
        short_title = row[3]
        text = row[4]
        days_till_due = row[5]
        print "%s %s" % (loc, days_till_due)
        try:
            st, created = Statute.objects.get_or_create(short_title=short_title, designator='', text=text, days_till_due=days_till_due)
        except Exception as e:
            st, created = Statute.objects.get_or_create(short_title=short_title, designator='', text=text)
            print e
        govt.statutes.add(st)
        idx += 1

def load_statutes():
    lagnuage, ntn, govt = get_defaults()

    st, created = Statute.objects.get_or_create(short_title='The Freedom of Information Act',\
    designator='552', text='a federal freedom of information law that allows for the\
     full or partial disclosure of previously unreleased information and documents\
    controlled by the United States government. ', days_till_due=20)
    st = Statute.objects.get(short_title="The Freedom of Information Act")
    govt.statutes.add(st)

    fee, created = FeeExemptionOther.objects.get_or_create(source='http://www.gwu.edu/~nsarchiv/nsa/foia/guide.html',\
     name='Fee Waiver - Commercial',
     description='Companies that or people who seek information for a use or purpose\
      that furthers commercial, trade, or profit interests,\
       including for use in litigation. Commercial requesters are required to pay for\
        search, review and duplication costs.', typee='F')
    st.fees_exemptions.add(fee)
    fee, created = FeeExemptionOther.objects.get_or_create(source='http://www.gwu.edu/~nsarchiv/nsa/foia/guide.html',\
     name='Fee Waiver - Educational Institution',
     description='Preschools, public or private elementary or secondary schools, and institutions\
      of graduate higher education, undergraduate higher education, professional education,\
       or vocational education that operate a program(s) of scholarly research.\
        Educational requesters are required to pay duplication costs, but are entitled\
         to the first 100 pages without charge.', typee='F')
    st.fees_exemptions.add(fee)
    fee, created = FeeExemptionOther.objects.get_or_create(source='http://www.gwu.edu/~nsarchiv/nsa/foia/guide.html',\
     name='Fee Waiver - Non-Commercial Scientific Institution',
     description=' Non-commercially operated institutions that conduct scientific research\
      not intended to promote any particular product or industry. Non-commercial requesters\
       are required to pay duplication costs, but are entitled to the first 100 pages without charge.', typee='F')
    st.fees_exemptions.add(fee)
    fee, created = FeeExemptionOther.objects.get_or_create(source='http://www.gwu.edu/~nsarchiv/nsa/foia/guide.html',\
     name='Fee Waiver - Representative of the News Media',
     description=' People who actively gather news for entities organized and operated to publish or broadcast\
      news to the public. News Media requesters are required to pay for duplication, but are\
       entitled to the first 100 pages without charge.', typee='F')
    st.fees_exemptions.add(fee)
    fee, created = FeeExemptionOther.objects.get_or_create(source='http://www.gwu.edu/~nsarchiv/nsa/foia/guide.html',\
     name='Fee Waiver - Other Requesters ',
     description='Requesters who do not fit into any of the above categories.\
      These requesters are persons who are not commercial, news media, scientific or\
       educational requesters and are required to pay search costs for more than 2 hours\
        and duplication costs for more than 100 pages.', typee='F')
    st.fees_exemptions.add(fee)

    exempt, created = FeeExemptionOther.objects.get_or_create(source='http://www.gwu.edu/~nsarchiv/nsa/foia/guide.html',\
     name='Exemption (b)(1)',
     description='National Security Information', typee='E')
    st.fees_exemptions.add(exempt)
    exempt, created = FeeExemptionOther.objects.get_or_create(source='http://www.gwu.edu/~nsarchiv/nsa/foia/guide.html',\
     name='Exemption (b)(2)',
     description='Internal Personnel Rules and Practices', typee='E')
    st.fees_exemptions.add(exempt)
    exempt, created = FeeExemptionOther.objects.get_or_create(source='http://www.gwu.edu/~nsarchiv/nsa/foia/guide.html',\
     name='Exemption (b)(2)-High',
     description='Substantial internal matters, disclosure would risk circumvention of a legal requirement', typee='E')
    st.fees_exemptions.add(exempt)
    exempt, created = FeeExemptionOther.objects.get_or_create(source='http://www.gwu.edu/~nsarchiv/nsa/foia/guide.html',\
     name='Exemption (b)(2)-Low',
     description='Internal matters that are essentially trivial in nature.', typee='E')
    st.fees_exemptions.add(exempt)
    exempt, created = FeeExemptionOther.objects.get_or_create(source='http://www.gwu.edu/~nsarchiv/nsa/foia/guide.html',\
     name='Exemption (b)(3)',
     description='Information exempt under other laws', typee='E')
    st.fees_exemptions.add(exempt)
    exempt, created = FeeExemptionOther.objects.get_or_create(source='http://www.gwu.edu/~nsarchiv/nsa/foia/guide.html',\
     name='Exemption (b)(4)',
     description='Confidential Business Information', typee='E')
    
    st.fees_exemptions.add(exempt)
    exempt, created = FeeExemptionOther.objects.get_or_create(source='http://www.gwu.edu/~nsarchiv/nsa/foia/guide.html',\
     name='Exemption (b)(5)',
     description='Inter or intra agency communication that is subject to deliberative process,\
      litigation, and other privileges', typee='E')
    st.fees_exemptions.add(exempt)
    exempt, created = FeeExemptionOther.objects.get_or_create(source='http://www.gwu.edu/~nsarchiv/nsa/foia/guide.html',\
     name='Exemption (b)(6)',
     description='Personal Privacy', typee='E')
    st.fees_exemptions.add(exempt)
    exempt, created = FeeExemptionOther.objects.get_or_create(source='http://www.gwu.edu/~nsarchiv/nsa/foia/guide.html',\
     name='Exemption (b)(7)',
     description='Law Enforcement Records that implicate one of 6 enumerated concerns', typee='E')
    st.fees_exemptions.add(exempt)
    exempt, created = FeeExemptionOther.objects.get_or_create(source='http://www.gwu.edu/~nsarchiv/nsa/foia/guide.html',\
     name='Exemption (b)(8)',
     description='Financial Institutions', typee='E')
    st.fees_exemptions.add(exempt)
    exempt, created = FeeExemptionOther.objects.get_or_create(source='http://www.gwu.edu/~nsarchiv/nsa/foia/guide.html',\
     name='Exemption (b)(9)',
     description='Geological Information', typee='E')
    st.fees_exemptions.add(exempt)

    govt = get_or_create_us_govt('California', 'state')
    st, created = Statute.objects.get_or_create(short_title='California Public Records Act',\
        designator='6250', text='A law passed by the California State Legislature\
         and signed by the Governor in 1968 requiring inspection and/or disclosure\
          of governmental records to the public upon request, unless exempted by law.', days_till_due=10)
    govt.statutes.add(st)

