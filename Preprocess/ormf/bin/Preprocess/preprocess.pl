#--------------------------------------------------------------------
# the pipeline for text preprocessing: tokenization, stemming, 
# removing non-words, 
#-------------------------------------------------------------------

use strict;
use warnings;
use FindBin;


die "Usage: perl bin/Preprocess/preprocess.pl input_file output_file" if (@ARGV != 2);

### 0. set up environment variables
my $home_dir = "$FindBin::Bin";
$home_dir =~ s/\/bin\/Preprocess$//;
if (defined $ENV{'PERL5LIB'}) {
    $ENV{'PERL5LIB'} = "$ENV{PERL5LIB}:$home_dir/lib/perl";
} else {
    $ENV{'PERL5LIB'} = "$home_dir/lib/perl";
}


my $prefix = $ARGV[0];
my $output_file = $ARGV[1];
my $clean = 1;

### 1. tokenize
my $cmd;
$cmd = "perl $home_dir/bin/Preprocess/tokenize_en.pl $prefix $prefix.tok";
print "\n[Step 1]: $cmd\n";
`$cmd`;
sleep(1);


### 2. stemming
$cmd = "cat $prefix.tok | perl $home_dir/bin/Preprocess/stemmer.pl > $prefix.stem";
print "\n[Step 2]: $cmd\n";
`$cmd`;
sleep(1);


### 3. clean the words
$cmd = "perl $home_dir/bin/Preprocess/clean.pl  $prefix.stem  $prefix.clean";
print "\n[Step 3]: $cmd\n";
`$cmd`;
sleep(1);


if ($clean == 1) {
    `rm  $prefix.tok  $prefix.stem`;
}

if ("$prefix.clean" ne $output_file) {
    `mv $prefix.clean $output_file`;
}
