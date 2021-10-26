# #flake8: noqa FE722
import re

from .results import Results
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

from app.logger import log


class Profile(Results):
    """Linkedin User Profile"""

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
        log(log.INFO, "Starting to determine the 'personal_info' of profile")
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
                "birth",
                "address",
                "twitter",
                "profile_url",
                "websites",
            ]
        )
        try:
            introductory_card = one_or_default(self.soup, ".pv-top-card")
            contact_info = one_or_default(self.soup, ".pv-contact-info")

            """Some of these selectors may have multiple selections, but get_info() takes the first match"""
            personal_info = {
                **personal_info,
                **get_info(
                    introductory_card,
                    {
                        "name": "h1",
                        "headline": ".text-body-medium.break-words",
                        "company": 'div[aria-label="Текущая компания"]',
                        "school": 'div[aria-label="Образование"]',
                        "location": ".text-body-small.inline.t-black--light.break-words",
                    },
                ),
            }

            summary = text_or_default(self.soup, ".pv-about-section", "").replace(
                # "... См. еще",
                "... see more",
                "",
            )

            personal_info["summary"] = re.sub(
                r"^About",
                # r"^Общие сведения", "", summary, flags=re.IGNORECASE
                "",
                summary,
                flags=re.IGNORECASE,
            ).strip()

            image_url = ""
            """If this is not None, you were scraping your own profile."""
            image_element = one_or_default(
                introductory_card, "img.profile-photo-edit__preview"
            )

            if not image_element:
                image_element = one_or_default(
                    introductory_card,
                    "img.pv-top-card-profile-picture__image.pv-top-card-profile-picture__image--show",
                )

            """Set image url to the src of the image html tag, if it exists"""
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
                # logger.info(
                #     "Found the Activity section, trying to determine follower count."
                # )

                # Search for numbers of the form xx(,xxx,xxx...)
                follower_count_search = re.search(
                    r"[^,\d](\d+(?:,\d{3})*) followers",
                    activity_section.text,
                    re.IGNORECASE,
                )

                if follower_count_search:
                    followers_text = follower_count_search.group(1)

                else:
                    # logger.debug("Did not find follower count")
                    pass
            else:
                # logger.info("Could not find the Activity section. Continuing anyways.")
                pass

            personal_info["followers"] = followers_text
            personal_info.update(
                get_info(
                    contact_info,
                    {
                        "profile_url": ".pv-contact-info__ci-container",
                        "email": ".ci-email .pv-contact-info__ci-container",
                        "phone": ".ci-phone .pv-contact-info__ci-container",
                        "connected": ".ci-connected .pv-contact-info__ci-container",
                        "twitter": ".ci-twitter .pv-contact-info__ci-container",
                        "birth": ".ci-birthday .pv-contact-info__ci-container",
                        "address": ".ci-address .pv-contact-info__ci-container",
                    },
                )
            )

            personal_info["websites"] = []
            if contact_info:
                websites = contact_info.select(".ci-websites li a")
                websites = list(map(lambda x: x["href"], websites))
                personal_info["websites"] = websites
        except Exception as e:
            log(
                log.EXCEPTION,
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
        log(log.INFO, "Trying to determine the 'experiences' property")
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
            log(
                log.EXCEPTION,
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
        log(log.INFO, "Trying to determine the 'skills' property")
        skills = self.soup.select(".pv-skill-category-entity__skill-wrapper")
        skills = list(map(get_skill_info, skills))

        """Sort skills based on endorsements."""

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
        log(log.INFO, "Trying to determine the 'accomplishments' property")
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
            log(
                log.EXCEPTION,
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
        log(log.INFO, "Trying to determine the 'interests' property")
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
            log(log.EXCEPTION, "Failed to get interests: %s", e)
        finally:
            return interests

    @property
    def recommendations(self):
        log(log.INFO, "Trying to determine the 'recommendations' property")
        recs = dict.fromkeys(["received", "given"], [])
        try:
            rec_block = one_or_default(self.soup, "section.pv-recommendations-section")
            received, given = all_or_default(rec_block, "div.artdeco-tabpanel")
            for rec_received in all_or_default(received, "li.pv-recommendation-entity"):
                recs["received"].append(get_recommendation_details(rec_received))

            for rec_given in all_or_default(given, "li.pv-recommendation-entity"):
                recs["given"].append(get_recommendation_details(rec_given))
        except Exception as e:
            log(log.EXCEPTION, "Failed to get recommendations: %s", e)
        finally:
            return recs

    def to_dict(self):
        log(log.INFO, "Attempting to turn return a dictionary for the Profile object.")
        return super(Profile, self).to_dict()
