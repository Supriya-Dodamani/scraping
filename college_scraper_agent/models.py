"""
models.py - Pydantic data models for college information
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class PlacementDetail(BaseModel):
    course: str = ""
    placement_percentage: Optional[float] = None
    average_salary_lpa: Optional[float] = None
    highest_salary_lpa: Optional[float] = None
    top_recruiters: List[str] = Field(default_factory=list)


class CourseDetail(BaseModel):
    name: str = ""           # MBA, MCA, BCA, BE, BTech, Diploma
    duration: str = ""       # e.g. "2 Years", "4 Years"
    total_seats: Optional[int] = None
    fee_per_year: Optional[float] = None
    specializations: List[str] = Field(default_factory=list)


class CollegeInfo(BaseModel):
    # Identity
    name: str = ""
    source_url: str = ""
    official_website: str = ""

    # Location
    address: str = ""
    city: str = ""
    state: str = ""
    pincode: str = ""

    # Contact
    phone_numbers: List[str] = Field(default_factory=list)
    emails: List[str] = Field(default_factory=list)

    # Leadership
    principal_name: str = ""
    chairman_name: str = ""

    # Academic
    affiliation: str = ""        # e.g. VTU, Mumbai University
    naac_grade: str = ""
    established_year: Optional[int] = None
    college_type: str = ""       # Government / Private / Deemed

    # Courses offered
    courses: List[CourseDetail] = Field(default_factory=list)
    courses_offered_names: List[str] = Field(default_factory=list)

    # Placements
    placements: List[PlacementDetail] = Field(default_factory=list)

    # Meta
    scrape_status: str = "pending"   # pending / success / failed
    scrape_errors: List[str] = Field(default_factory=list)

    def to_flat_dict(self) -> dict:
        """Returns a flat dict suitable for CSV export."""
        phones = " | ".join(self.phone_numbers)
        emails = " | ".join(self.emails)
        courses = " | ".join(self.courses_offered_names)

        placement_summary = []
        for p in self.placements:
            s = f"{p.course}: {p.placement_percentage or 'N/A'}% placed"
            if p.average_salary_lpa:
                s += f", Avg {p.average_salary_lpa} LPA"
            if p.highest_salary_lpa:
                s += f", Highest {p.highest_salary_lpa} LPA"
            placement_summary.append(s)

        top_recruiters = []
        for p in self.placements:
            top_recruiters.extend(p.top_recruiters)
        top_recruiters = list(set(top_recruiters))

        return {
            "College Name": self.name,
            "City": self.city,
            "State": self.state,
            "Address": self.address,
            "Pincode": self.pincode,
            "Phone Numbers": phones,
            "Emails": emails,
            "Principal Name": self.principal_name,
            "Affiliation": self.affiliation,
            "NAAC Grade": self.naac_grade,
            "College Type": self.college_type,
            "Courses Offered": courses,
            "Placement Summary": " || ".join(placement_summary),
            "Top Recruiters": " | ".join(top_recruiters[:10]),
            "Official Website": self.official_website,
            "Source URL": self.source_url,
        }
