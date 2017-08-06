#---------------------------------------------------------
# transform words to index
#---------------------------------------------------------

use strict;
use warnings;
use Preprocess::IndexWord;

die "Usage: perl index.pl is_train input_file output_file vocab_file" if (@ARGV != 4);
my $is_train = $ARGV[0];
my $input_file = $ARGV[1];
my $output_file = $ARGV[2];
my $vocab_file = $ARGV[3];

my $index_word = Preprocess::IndexWord->new($vocab_file, $is_train);
$index_word->query("#gww#", $is_train); # index start from 1

open(I, $input_file) || die "Cannot open $input_file\n";
open(O, ">$output_file") || die "Cannot open $output_file\n";

while (my $str = <I>) {
    $str =~ s/\s+$//;
    my @tokens = split(/\s+/, $str);
    foreach my $t (@tokens) {
	next if ($t =~ /^\s*$/);
	my $index = $index_word->query($t, $is_train);
	print O "$index " if ($index != -1);
    }
    print O "\n";
}

