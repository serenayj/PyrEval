#-------------------------------------
# change data into matlab sparse matrix format
#-------------------------------------

use strict;
use warnings;

die "Usage:  perl  matlab_format.pl  input_file  output_file\n" if (@ARGV != 2);

my $input_file = $ARGV[0];
my $output_file = $ARGV[1];

open(I, $input_file) || die "Cannot open $input_file\n";
open(O, ">$output_file") || die "Cannot create $output_file\n";

print "$input_file\n";
my $line = 1;
while (my $str = <I>) {
    $str =~ s/\s+$//;
    my @tokens = split(/\s+/, $str);
    for (my $i = 0; $i < @tokens; $i=$i+2) {
	print O $tokens[$i]."\t$line\t$tokens[$i+1]\n";
    }
    $line++;
}
