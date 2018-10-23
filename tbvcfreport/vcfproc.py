"""
Interface to handle VCF files
"""
import sys
import vcf
from tqdm import tqdm

try:
    from .dbconn import get_gene_data, graph
except (ImportError, ValueError):
    from dbconn import get_gene_data, graph


class VCFProc(object):
    """
    Process VCF File
    """

    def __init__(self, vcf_file):
        self.vcf_file = vcf_file

    def parse(self):
        variants, rv_tags = [], []
        if self.vcf_file.endswith(".vcf"):
            sys.stdout.write(
                "Using: {}...\n".format(graph))
            sys.stdout.write(
                "Processing: {}...\n".format(self.vcf_file))
            with open(self.vcf_file) as _vcf:
                vcf_reader = vcf.Reader(_vcf)
                for record in tqdm(vcf_reader):
                    if record.var_type == 'snp':
                        record.affected_start += 1
                    affected_region = "..".join(
                        [str(record.affected_start), str(record.affected_end)])
                    # Usually there is more than one annotation reported in
                    # each ANN. A variant can affect multiple genes
                    if record.INFO.get('ANN'):
                        annotations = self.get_variant_ann(record=record)
                        for annotation in annotations:
                            gene_identifier = annotation[4]
                            # TODO: It is much faster to issue 1 query
                            rv_tags.append(gene_identifier)
                            variant_data = self.get_variant_data(
                                gene_identifier)
                            annotation.extend(
                                [record.CHROM, record.POS, record.REF,
                                 record.var_type, affected_region,
                                 variant_data])
                            variants.append(annotation)
        else:
            sys.stderr.write("Can't parse {vcf_file}".format(
                vcf_file=self.vcf_file))
        return variants

    @staticmethod
    def get_variant_ann(record):
        """
        Get Annotation from ANN
        :param record:
        :return:
        """
        annotations = []
        if record.INFO.get('ANN'):
            annotations = [ann.split("|") for ann in record.INFO['ANN']]
        return annotations

    @staticmethod
    def get_variant_data(entry):
        """
        Get variant data from DB
        :param entry:
        :return:
        """
        data = get_gene_data(entry)
        return data
