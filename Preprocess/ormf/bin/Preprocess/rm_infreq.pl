#---------------------------------------------
# remove infrequent words (less than a threshold) in reviews
#---------------------------------------------

use strict;
use warnings;

die "perl rm_infreq.pl input_file output_file threshold" if (@ARGV != 3);

my $threshold = $ARGV[2];
#my $input_file = "data/zagat/text/lemma/review.merge.nosw";
#my $output_file = "data/zagat/text/lemma/review.merge.nosw.f$threshold";
my $input_file = $ARGV[0];
my $output_file = $ARGV[1];


open(I, $input_file) || die "Cannot open $input_file\n";
open(O, ">$output_file") || die "Cannot create $output_file\n";


my @strs = <I>;
my %freq;
foreach my $str (@strs) {
    $str =~ s/\s+$//;
    my @tokens = split(/\s+/, $str);
    foreach my $token (@tokens) {
	$freq{$token}++;
    }
}

foreach my $str (@strs) {
    $str =~ s/\s+$//;
    my @tokens = split(/\s+/, $str);
    foreach my $token (@tokens) {
	if ($freq{$token} >= $threshold) {
	    print O "$token ";
	}
    }
    print O "\n";
}

close(I);
close(O);
