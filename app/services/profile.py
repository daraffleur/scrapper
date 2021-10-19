# #flake8: noqa FE722
import re
import logging
from typing import List

from .ResultsObject import ResultsObject
from app.utils import (
    one_or_default,
    get_info,
    text_or_default,
    all_or_default,
    flatten_list,
    get_job_info,
    get_school_info,
    get_volunteer_info,
    get_skill_info,
    get_recommendation_details,
)

# from app.logger import log


logger = logging.getLogger(__name__)


class Profile(ResultsObject):
    """Linkedin User Profile Object"""

    attributes = [
        "personal_info",
        "experiences",
        "skills",
        "accomplishments",
        "interests",
        "recommendations",
    ]

    @property
    def personal_info(self):
        logger.info("Trying to determine the 'personal_info' property")
        """Return dict of personal info about the user"""
        personal_info = dict.fromkeys(
            [
                "name",
                "headline",
                "company",
                "school",
                "location",
                "summary",
                "image",
                "followers",
                "email",
                "phone",
                "connected",
                "websites",
            ]
        )
        try:
            top_card = one_or_default(self.soup, ".pv-top-card")
            contact_info = one_or_default(self.soup, ".pv-contact-info")

            # Note that some of these selectors may have multiple selections, but
            # get_info takes the first match
            personal_info = {
                **personal_info,
                **get_info(
                    top_card,
                    {
                        "name": "h1",
                        "headline": ".text-body-medium.break-words",
                        "company": 'div[aria-label="Current company"]',
                        "school": 'div[aria-label="Education"]',
                        "location": ".text-body-small.inline.break-words",
                    },
                ),
            }

            summary = text_or_default(self.soup, ".pv-about-section", "").replace(
                "... see more", ""
            )

            personal_info["summary"] = re.sub(
                r"^About", "", summary, flags=re.IGNORECASE
            ).strip()

            image_url = ""
            # If this is not None, you were scraping your own profile.
            image_element = one_or_default(top_card, "img.profile-photo-edit__preview")

            if not image_element:
                image_element = one_or_default(top_card, "img.pv-top-card__photo")

            # Set image url to the src of the image html tag, if it exists
            try:
                image_url = image_element["src"]
            except:
                pass

            personal_info["image"] = image_url

            activity_section = one_or_default(
                self.soup, ".pv-recent-activity-section-v2"
            )

            followers_text = ""
            if activity_section:
                logger.info(
                    "Found the Activity section, trying to determine follower count."
                )

                # Search for numbers of the form xx(,xxx,xxx...)
                follower_count_search = re.search(
                    r"[^,\d](\d+(?:,\d{3})*) followers",
                    activity_section.text,
                    re.IGNORECASE,
                )

                if follower_count_search:
                    followers_text = follower_count_search.group(1)

                else:
                    logger.debug("Did not find follower count")
            else:
                logger.info("Could not find the Activity section. Continuing anyways.")

            personal_info["followers"] = followers_text
            personal_info.update(
                get_info(
                    contact_info,
                    {
                        "email": ".ci-email .pv-contact-info__ci-container",
                        "phone": ".ci-phone .pv-contact-info__ci-container",
                        "connected": ".ci-connected .pv-contact-info__ci-container",
                    },
                )
            )

            personal_info["websites"] = []
            if contact_info:
                websites = contact_info.select(".ci-websites li a")
                websites = list(map(lambda x: x["href"], websites))
                personal_info["websites"] = websites
        except Exception as e:
            logger.exception(
                "Encountered error while fetching personal_info. Details may be incomplete/missing/wrong: %s",
                e,
            )
        finally:
            return personal_info

    @property
    def experiences(self):
        """
        Returns:
            dict of person's professional experiences.  These include:
                - Jobs
                - Education
                - Volunteer Experiences
        """
        logger.info("Trying to determine the 'experiences' property")
        experiences = dict.fromkeys(["jobs", "education", "volunteering"], [])
        try:
            container = one_or_default(self.soup, ".background-section")

            jobs = all_or_default(
                container, "#experience-section ul .pv-position-entity"
            )
            jobs = list(map(get_job_info, jobs))
            jobs = flatten_list(jobs)

            experiences["jobs"] = jobs

            schools = all_or_default(
                container, "#education-section .pv-education-entity"
            )
            schools = list(map(get_school_info, schools))
            experiences["education"] = schools

            volunteering = all_or_default(
                container,
                ".pv-profile-section.volunteering-section .pv-volunteering-entity",
            )
            volunteering = list(map(get_volunteer_info, volunteering))
            experiences["volunteering"] = volunteering
        except Exception as e:
            logger.exception(
                "Failed while determining experiences. Results may be missing/incorrect: %s",
                e,
            )
        finally:
            return experiences

    @property
    def skills(self):
        """
        Returns:
            list of skills {name: str, endorsements: int} in decreasing order of
            endorsement quantity.
        """
        logger.info("Trying to determine the 'skills' property")
        skills = self.soup.select(".pv-skill-category-entity__skill-wrapper")
        skills = list(map(get_skill_info, skills))

        # Sort skills based on endorsements.  If the person has no endorsements
        def sort_skills(x):
            return int(x["endorsements"].replace("+", "")) if x["endorsements"] else 0

        return sorted(skills, key=sort_skills, reverse=True)

    @property
    def accomplishments(self):
        """
        Returns:
            dict of professional accomplishments including:
                - publications
                - cerfifications
                - patents
                - courses
                - projects
                - honors
                - test scores
                - languages
                - organizations
        """
        logger.info("Trying to determine the 'accomplishments' property")
        accomplishments = dict.fromkeys(
            [
                "publications",
                "certifications",
                "patents",
                "courses",
                "projects",
                "honors",
                "test_scores",
                "languages",
                "organizations",
            ]
        )
        try:
            container = one_or_default(self.soup, ".pv-accomplishments-section")
            for key in accomplishments:
                accs = all_or_default(container, "section." + key + " ul > li")
                accs = map(lambda acc: acc.get_text() if acc else None, accs)
                accomplishments[key] = list(accs)
        except Exception as e:
            logger.exception(
                "Failed to get accomplishments, results may be incomplete/missing/wrong: %s",
                e,
            )
        finally:
            return accomplishments

    @property
    def interests(self):
        """
        Returns:
            list of person's interests
        """
        logger.info("Trying to determine the 'interests' property")
        interests = []
        try:
            container = one_or_default(self.soup, ".pv-interests-section")
            interests = all_or_default(container, "ul > li")
            interests = list(
                map(
                    lambda i: text_or_default(i, ".pv-entity__summary-title"), interests
                )
            )
        except Exception as e:
            logger.exception("Failed to get interests: %s", e)
        finally:
            return interests

    @property
    def recommendations(self):
        logger.info("Trying to determine the 'recommendations' property")
        recs = dict.fromkeys(["received", "given"], [])
        try:
            rec_block = one_or_default(self.soup, "section.pv-recommendations-section")
            received, given = all_or_default(rec_block, "div.artdeco-tabpanel")
            for rec_received in all_or_default(received, "li.pv-recommendation-entity"):
                recs["received"].append(get_recommendation_details(rec_received))

            for rec_given in all_or_default(given, "li.pv-recommendation-entity"):
                recs["given"].append(get_recommendation_details(rec_given))
        except Exception as e:
            logger.exception("Failed to get recommendations: %s", e)
        finally:
            return recs

    def to_dict(self):
        logger.info("Attempting to turn return a dictionary for the Profile object.")
        return super(Profile, self).to_dict()


# # from typing import List

# from bs4 import BeautifulSoup

# # from app.logger import log


# class Profile:
#     """LinkedIn User Profile Object"""

#     def __init__(self):
#         self.soup = None

#     def get_soup(self, html):
#         self.soup = BeautifulSoup(html, "lxml")

#     def get_contact_info(self, content):
#         html = BeautifulSoup(content.get_attribute("innerHTML"), "lxml")

#         email = self.get_email(html)
#         birth_day = self.get_birth_day(html)
#         return [email, birth_day]

#     def get_introduction(self):
#         name = self.get_full_name()
#         description = self.get_description()
#         location = self.get_location()
#         return [name, description, location]

#     def get_email(self, html):
#         """Extract email"""
#         email_class = html.find("section", {"class": "ci-email"})
#         if email_class:
#             email_loc = email_class.find("a")
#             return email_loc.get_text().strip()
#         else:
#             return ""

#     def get_birth_day(self, html):
#         """Extract date of birth"""
#         birth_class = html.find("section", {"class": "ci-birthday"})
#         if birth_class:
#             birth_loc = birth_class.find(
#                 "span",
#             )
#             return birth_loc.get_text().strip()
#         else:
#             return ""

#     def get_full_name(self):
#         """Extract profile name"""
#         introduction = self.soup.find("div", {"class": "pv-text-details__left-panel"})
#         name_loc = introduction.find("h1")
#         return name_loc.get_text().strip()

#     def get_description(self):
#         """Extract profile description"""
#         introduction = self.soup.find("div", {"class": "pv-text-details__left-panel"})
#         desc_loc = introduction.find("div", {"class": "text-body-medium"})
#         return desc_loc.get_text().strip()

#     def get_location(self):
#         """Extract location"""
#         location_div = self.soup.find(
#             "div", {"class": "pb2 pv-text-details__left-panel"}
#         )
#         location_loc = location_div.find_all("span", {"class": "text-body-small"})
#         return location_loc[0].get_text().strip()
