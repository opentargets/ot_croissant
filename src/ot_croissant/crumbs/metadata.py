"""Classes for overall OT Platform metadata."""
import logging
from mlcroissant import Metadata
from ot_croissant.crumbs.distribution import PlatformOutputDistribution
from ot_croissant.crumbs.record_sets import PlatformOutputRecordSets
from ot_croissant.curation import InstanceCuration

logger = logging.getLogger(__name__)

class PlatformOutputMetadata(Metadata):
    """Class extending the Metadata class from MLCroissant to define the OT Platform metadata."""

    CITE_AS = r"@article{PMID:39657122, author = {Buniello, Annalisa and Suveges, Daniel and Cruz-Castillo, Carlos and  Llinares, Manuel Bernal and Cornu, Helena and Lopez, Irene and Tsukanov, Kirill and Rold{'a}n-Romero, Juan Mar{'\i}a and Mehta, Chintan and Fumis, Luca and McNeill, Graham and Hayhurst, James D and Martinez Osorio, Ricardo Esteban and Barkhordari, Ehsan and Ferrer, Javier and Carmona, Miguel and Uniyal, Prashant and Falaguera, Maria J and Rusina, Polina and Smit, Ines and Schwartzentruber, Jeremy and Alegbe, Tobi and Ho, Vivien W and Considine, Daniel and Ge, Xiangyu and Szyszkowski, Szymon and Tsepilov, Yakov and Ghoussaini, Maya and Dunham, Ian and Hulcoop, David G and McDonagh, Ellen M and Ochoa, David}, title = {{Open Targets Platform: facilitating therapeutic hypotheses building in drug discovery.}}, journal = {Nucleic Acids Res}, year = {2025}, volume = {53}, number = {D1}, pages = {D1467--D1475}, month = jan, affiliation = {Open Targets, Wellcome Genome Campus, Hinxton, Cambridgeshire CB10 1SD, UK.}, doi = {10.1093/nar/gkae1128}, pmid = {39657122}, pmcid = {PMC11701534}, date-added = {2024-12-16T14:58:07GMT}, date-modified = {2025-02-13T11:33:43GMT}, abstract = {The Open Targets Platform (https://platform.opentargets.org) is a unique, open-source, publicly-available knowledge base providing data and tooling for systematic drug target identification, annotation, and prioritisation. Since our last report, we have expanded the scope of the Platform through a number of significant enhancements and data updates, with the aim to enable our users to formulate more flexible and impactful therapeutic hypotheses. In this context, we have completely revamped our target-disease associations page with more interactive facets and built-in functionalities to empower users with additional control over their experience using the Platform, and added a new Target Prioritisation view. This enables users to prioritise targets based upon clinical precedence, tractability, doability and safety attributes. We have also implemented a direction of effect assessment for eight sources of target-disease association evidence, showing the effect of genetic variation on the function of a target is associated with risk or protection for a trait to inform on potential mechanisms of modulation suitable for disease treatment. These enhancements and the introduction of new back and front-end technologies to support them have increased the impact and usability of our resource within the drug discovery community.},}"


    def __init__(
        self,
        datasets: list[str],
        ftp_location: str | None,
        gcp_location: str,
        version: str,
        date_published: str,
        data_integrity_hash: str,
        instance: str | None = None
    ):
        """Initialize the metadata."""
        # Managing instance:
        if instance != 'ppp':
            instance = 'public'

        logger.info(f'Generating metadata for the {instance} Platform instance.')
        curation = InstanceCuration()

        super().__init__(
            name=curation.get_curation(instance, 'name'),
            description=curation.get_curation(instance, 'description'),
            cite_as=self.CITE_AS,
            url=curation.get_curation(instance, 'url'),
            license=curation.get_curation(instance, 'license'),
            version=version,
            date_published=date_published,
            distribution=(
                PlatformOutputDistribution()
                .add_ftp_location(ftp_location, data_integrity_hash)
                .add_gcp_location(gcp_location, data_integrity_hash)
                .add_assets_from_paths(paths=datasets)
                .get_metadata()
            ),
            record_sets=PlatformOutputRecordSets()
            .add_assets_from_paths(paths=datasets)
            .get_metadata(),
        ) 
